"""
Module used to configure the Celery worker for the backend.
"""

import asyncio
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, BinaryIO

from asgiref.sync import async_to_sync
from celery import Celery, Task, states
from pymongo.asynchronous.database import AsyncDatabase

from backend.configs import BackendSettings
from backend.database.configs import DatabaseConfig
from backend.database.enums import PyObjectId

# Setup Celery application.
__CELERY_BROKER_URL__ = f"{BackendSettings.redis_uri}:{BackendSettings.redis_port}/{BackendSettings.redis_db}"
app = Celery(main="ai_annotator_worker", broker=__CELERY_BROKER_URL__, backend=__CELERY_BROKER_URL__)


# Classes.
class WorkerUploadFile:
    """
    Class to represent the UploadFile schema from FastAPI in the Celery worker.
    """

    # Special methods.
    def __init__(self, temp_file_path: str, filename: str, content_type: str, **kwargs) -> None:

        # Attributes.
        self.file_path = temp_file_path
        self.filename = filename
        self.content_type = content_type
        self.__file: BinaryIO | None = None
        self.__extra_kwargs = kwargs

    def __enter__(self):
        """
        Method to enter the context of the UploadFile.

        Returns:
            WorkerUploadFile: The WorkerUploadFile instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Method to exit the context of the UploadFile.

        Args:
            exc_type: The exception type.
            exc_val: The exception value.
            exc_tb: The exception traceback.
        """
        self.close()

    def __del__(self):
        """
        Method to delete the WorkerUploadFile instance and remove the temporary file from disk.
        """
        self.close()

    # Properties.
    @property
    def file(self) -> BinaryIO:
        """
        Property to get the file content.

        Returns:
            BinaryIO: The file content.
        """
        if self.__file is None:
            if self.file_path and os.path.exists(path=self.file_path):
                self.__file = open(file=self.file_path, mode="rb")
            else:
                raise FileNotFoundError(f"File not found at path: {self.file_path}")
        return self.__file

    @property
    def size(self) -> int:
        """
        Property to get the file size.

        Returns:
            int: The file size in bytes.
        """
        file = self.file  # type: ignore
        current_pos = file.tell()
        file.seek(0, 2)  # Seek to the end of the file.
        size = file.tell()  # Get the current position (i.e., the size).
        file.seek(current_pos)  # Reset the file pointer to the original position.
        return size

    # Methods.
    def close(self) -> None:
        """
        Method to close the WorkerUploadFile instance and remove the temporary file from disk.
        """
        # Close the file if it's open.
        if self.__file:
            try:
                self.__file.close()  # type: ignore
            finally:
                self.__file = None

        # Delete the temporary file from disk.
        if self.file_path and os.path.exists(path=self.file_path):
            try:
                os.unlink(path=self.file_path)  # Remove the temporary file from disk.
            except OSError:
                pass
        self.file_path = ""  # Clear the file path to prevent further access.

    def get(self, key: str) -> Any | None:
        """
        Method to get extra keyword arguments passed during initialization.

        Args:
            key (str): The key of the extra keyword argument to get.

        Returns:
            Any | None: The value of the extra keyword argument.
        """
        return self.__extra_kwargs.get(key)  # type: ignore


class UpdateTaskState(ABC):
    """
    Abstract base class to represent the state of a Celery task for processing uploaded files. This class is used to
    update the task state and progress during the file processing.
    """

    # Special methods.
    def __init__(self, task: Task) -> None:
        self.__task = task

    # Abstract methods.
    @abstractmethod
    def update_state(self, state: str, message: str, *args, **kwargs):
        pass

    # Properties.
    @property
    def task(self) -> Task:
        """
        Property to get the Celery task instance.

        Returns:
            Task: The Celery task instance.
        """
        return self.__task


class UpdateProcessUploadedFileTaskState(UpdateTaskState):
    """
    Class to represent the state of the Celery task for processing uploaded files. This class is used to update the
    task state and progress during the file processing.
    """

    def update_state(
        self,
        state: str = states.STARTED,
        message: str = "Processing uploaded files...",
        number_processed_files: int = 0,
        total_number_of_files: int = 0,
        number_of_successfully_processed_files: int = 0,
        number_of_failed_files: int = 0,
    ) -> None:
        self.task.update_state(
            state=state,
            meta={
                "current": number_processed_files,
                "total": total_number_of_files,
                "number_of_successfully_processed_files": number_of_successfully_processed_files,
                "number_of_failed_files": number_of_failed_files,
                "message": message,
            },
        )


# Functions.
def _run_worker_in_threading(wrapper_func: Callable, *args, **kwargs) -> Any:
    """
    Utility function to run the Celery worker in a separate thread. This is used to execute the worker tasks
    during tests without blocking the main test thread and event loop.

    Args:
        wrapper_func (Callable): The wrapper function to run the worker.
    """

    def _thread_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)
        try:
            return loop.run_until_complete(future=wrapper_func(*args, **kwargs))
        finally:
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_thread_wrapper)
        return future.result()


# Tasks.
@app.task(bind=True, name="process_uploaded_file")
def process_uploaded_file_task(self, temp_file_list: list[dict], project_id: str | PyObjectId) -> list[dict]:
    """
    Celery task to process an uploaded file.

    Args:
        temp_file_list (list[dict]): The list of temporary file paths to process.
        project_id (str | PyObjectId): The ID of the project the files belong to.
    """

    # Async function to process the uploaded file.
    async def wrapper(is_eager: bool = False) -> list[dict]:

        # Import function inside the task.
        from backend.api.v1.utils.files import create_file_records

        # Instantiate the database connection for the worker.
        db: AsyncDatabase = await DatabaseConfig.get_local_database()  # type: ignore

        # Instantiate the WorkerUploadFile objects.
        worker_file_list = [WorkerUploadFile(**temp_file) for temp_file in temp_file_list]

        # Instantiate the task state updater.
        if is_eager:
            state_updater: UpdateProcessUploadedFileTaskState | None = None
        else:
            state_updater: UpdateProcessUploadedFileTaskState = UpdateProcessUploadedFileTaskState(task=self)  # type: ignore

        # Process the files and create the file records in the database.
        try:
            created_file_records = await create_file_records(
                file_list=worker_file_list, project_id=project_id, db=db, state_updater=state_updater
            )  # type: ignore
            if state_updater:
                state_updater.update_state(state=states.SUCCESS, message="Finished processing uploaded files.")
            return created_file_records
        except Exception as e:
            if state_updater:
                state_updater.update_state(state=states.FAILURE, message=f"Failed to process uploaded files. {str(e)}")
            raise e
        finally:
            await db.client.close()  # type: ignore  # Close the database client after processing to avoid sharing the same client instance across multiple worker processes.

    # Check if the task is running in eager mode (i.e., during tests) and execute the wrapper function accordingly.
    if self.request.is_eager:
        return _run_worker_in_threading(wrapper_func=wrapper, is_eager=True)
    return async_to_sync(wrapper)()
