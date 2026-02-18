"""
Module used to configure the Celery worker for the backend.
"""

from typing import BinaryIO

from celery import Celery
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.utils.files import create_file_records
from backend.configs import BackendSettings
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


# Tasks.
@app.task(name="process_uploaded_file")
async def process_uploaded_file_task(
    self, temp_file_list: list[dict], project_id: str | PyObjectId, db: AsyncDatabase
) -> list[dict]:
    """
    Celery task to process an uploaded file.

    Args:
        temp_file_list (list[dict]): The list of temporary file paths to process.
        project_id (str | PyObjectId): The ID of the project the files belong to.
        db (AsyncDatabase): The database instance.
    """
    # Instantiate the WorkerUploadFile objects.
    worker_file_list = [WorkerUploadFile(**temp_file) for temp_file in temp_file_list]

    # Process the files and create the file records in the database.
    created_file_records = await create_file_records(file_list=worker_file_list, project_id=project_id, db=db)  # type: ignore
    return created_file_records
