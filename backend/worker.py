"""
Module used to configure the Celery worker for the backend.
"""

import asyncio
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, BinaryIO

from asgiref.sync import async_to_sync
from celery import Celery
from pymongo.asynchronous.database import AsyncDatabase

from backend.configs import BackendSettings
from backend.database.configs import DatabaseConfig
from backend.database.enums import PyObjectId

# Setup Celery application.
__CELERY_BROKER_URL__ = f"{BackendSettings.redis_uri}:{BackendSettings.redis_port}/{BackendSettings.redis_db}"
app = Celery(main="ai_annotator_worker", broker=__CELERY_BROKER_URL__, backend=__CELERY_BROKER_URL__)


# Schemas.
class WorkerUploadFile:
    """
    Class to represent the UploadFile schema from FastAPI in the Celery worker.
    """

    # Special methods.
    def __init__(self, temp_file_path: str, filename: str, content_type: str) -> None:

        # Attributes.
        self.file_path = temp_file_path
        self.filename = filename
        self.content_type = content_type
        self.__file: BinaryIO | None = None

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
            self.__file = open(file=self.file_path, mode="rb")
        return self.__file

    @property
    def size(self) -> int:
        """
        Property to get the file size.

        Returns:
            int: The file size in bytes.
        """
        file = self.file  # type: ignore
        file.seek(0, 2)  # Seek to the end of the file.
        size = file.tell()  # Get the current position (i.e., the size).
        file.seek(0)  # Reset the file pointer to the beginning.
        return size

    # Methods.
    def close(self) -> None:
        """
        Method to close the WorkerUploadFile instance and remove the temporary file from disk.
        """
        if self.__file:
            self.__file.close()  # type: ignore
            os.unlink(path=self.file_path)  # Remove the temporary file from disk.


# Functions.
def _run_worker_in_threading(wrapper_func: Callable) -> Any:
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
            return loop.run_until_complete(future=wrapper_func())
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
    async def wrapper() -> list[dict]:

        # Import function inside the task.
        from backend.api.v1.utils.files import create_file_records

        # Instantiate the database connection for the worker.
        db: AsyncDatabase = await DatabaseConfig.get_local_database()  # type: ignore

        # Instantiate the WorkerUploadFile objects.
        worker_file_list = [WorkerUploadFile(**temp_file) for temp_file in temp_file_list]

        # Process the files and create the file records in the database.
        created_file_records = await create_file_records(file_list=worker_file_list, project_id=project_id, db=db)  # type: ignore
        return created_file_records

    # Check if the task is running in eager mode (i.e., during tests) and execute the wrapper function accordingly.
    if self.request.is_eager:
        return _run_worker_in_threading(wrapper_func=wrapper)
    return async_to_sync(wrapper)()
