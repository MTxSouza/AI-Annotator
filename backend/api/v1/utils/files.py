"""
Module with all utilities related to file operations.
"""
import hashlib
import shutil
import uuid
from pathlib import Path
from typing import Generator

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.files import (AudioFile_Create, ImageFile_Create,
                                         TextFile_Create, UploadedFileResponse)
from backend.database.configs import Collections
from backend.database.types import FileFormat, FileUploadStatus, PyObjectId

# Global variables.
STATIC_FILE_DIRECTORY = "/app/storage"
FILE_CHUNK_SIZE = 64 * 1024  # 64 KB

# Functions.
def generate_unique_filename(
    file_format: FileFormat
    ) -> str:
    """
    Utility function to generate a unique filename.

    Args:
        file_format (FileFormat): The format of the file.

    Returns:
        str: The generated unique filename.
    """
    # Generate a unique identifier.
    unique_id = str(uuid.uuid4())

    # Add file extension based on the file format.
    file_extension = file_format.value.lower()
    unique_filename = "%s.%s" % (unique_id, file_extension)
    return unique_filename

def load_upload_file_in_chunks(
    file: UploadFile
    ) -> Generator[bytes, None, None]:
    """
    Generator to load an upload file in chunks.

    Args:
        file (UploadFile): The upload file to load in chunks.

    Yields:
        bytes: The next chunk of the file.
    """
    # Move cursor to the beginning of the file.
    file.file.seek(0)

    # Read file in chunks to avoid memory issues.
    while chunk := file.file.read(FILE_CHUNK_SIZE):
        yield chunk

def get_upload_file_hash(
    file: UploadFile
    ) -> str:
    """
    Utility function to compute the hash of an upload file.

    Args:
        file (UploadFile): The upload file to compute the hash for.

    Returns:
        str: The computed hash of the upload file.
    """
    # Define hash object.
    sha256_hash = hashlib.sha256()

    # Load file in chunks to avoid memory issues.
    for chunk in load_upload_file_in_chunks(file):
        sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

def get_file_metadata(
    file: UploadFile
    ) -> dict:
    """
    Utility function to get metadata of an upload file.

    Args:
        file (UploadFile): The upload file to get metadata for.

    Returns:
        dict: Metadata of the upload file.
    """
    # Get file extension.
    file_size = file.size
    file_extension = file.content_type.split(sep="/")[-1].lower()
    return {"format": file_extension, "size_in_bytes": file_size}

def save_upload_file_to_disk(
    file: UploadFile,
    unique_filename: str
    ) -> None:
    """
    Utility function to save the upload file to disk.

    Args:
        file (UploadFile): The upload file to save.
        unique_filename (str): The unique filename to save the file as.
    """
    # Move cursor to the beginning of the file.
    file.file.seek(0)

    # Save file in chunks to avoid memory issues.
    with Path(STATIC_FILE_DIRECTORY, unique_filename).open(mode="wb") as file_buffer:
        shutil.copyfileobj(fsrc=file.file, fdst=file_buffer)

async def get_files(
    limit: int,
    offset: int,
    db: AsyncDatabase
    ) -> list[dict]:
    """
    Utility function to get all files from the database.

    Args:
        limit (int): The maximum number of files to retrieve.
        offset (int): The number of files to skip.
        db (AsyncDatabase): The database instance.

    Returns:
        list[dict]: List of all files.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Query files.
    cursor = collection.find().skip(offset).limit(limit)
    files = await cursor.to_list()

    return files

async def get_file_by_it_hash(
    file_hash: str,
    db: AsyncDatabase
    ) -> dict | None:
    """
    Utility function to get a file from the database by its hash.

    Args:
        file_hash (str): The hash of the file to retrieve.
        db (AsyncDatabase): The database instance.

    Returns:
        dict | None: The file document if found, None otherwise.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Query file by its hash.
    file_document = await collection.find_one({"file_hash": file_hash})
    return file_document

async def is_file_exists(
    file: UploadFile,
    db: AsyncDatabase
    ) -> bool:
    """
    Utility function to check if an upload file exists in the database by its hash.

    Args:
        file (UploadFile): The upload file to check.
        db (AsyncDatabase): The database instance.

    Returns:
        bool: True if the upload file exists, False otherwise.
    """
    # Get file hash.
    file_hash = await run_in_threadpool(func=get_upload_file_hash, file=file)

    # Get file by its hash.
    existing_file = await get_file_by_it_hash(file_hash=file_hash, db=db)
    return existing_file is not None

def _sync_check_image_corruption(
    file: UploadFile
    ) -> bool:
    """
    Synchronous utility function to check if an image file is corrupted.

    Args:
        file (UploadFile): The upload file to check.

    Returns:
        bool: True if the image file is corrupted, False otherwise.
    """
    try:
        with Image.open(fp=file.file) as img_buffer:
            img_buffer.verify()
        return False
    except (UnidentifiedImageError, OSError):
        return True

def _sync_get_image_metadata(
    file: UploadFile
    ) -> dict:
    """
    Synchronous utility function to get metadata of an image upload file.

    Args:
        file (UploadFile): The upload file to get metadata for.

    Returns:
        dict: Metadata of the upload file.
    """
    # Get file extension.
    file_size = file.size
    file_extension = file.content_type.split(sep="/")[-1].lower()

    # Get image dimensions.
    with Image.open(fp=file.file) as img_buffer:
        width, height = img_buffer.size
        channels = len(img_buffer.getbands())

    return {
        "format": file_extension,
        "size_in_bytes": file_size,
        "width": width,
        "height": height,
        "channels": channels
    }

async def process_image_record(
    file: UploadFile,
    file_metadata: dict,
    file_hash: str,
    project_id: str,
    db: AsyncDatabase
    ) -> UploadedFileResponse:
    """
    Utility function to process an image file and create its record in the database.

    Args:
        file (UploadFile): The upload file to process.
        file_metadata (dict): The metadata of the upload file.
        file_hash (str): The hash of the upload file.
        project_id (str): The project ID associated with the file.
        db (AsyncDatabase): The database instance.

    Returns:
        UploadedFileResponse: The response model for the uploaded image file.
    """
    # Check project ID type.
    if isinstance(project_id, str):
        project_id = PyObjectId(oid=project_id)

    # Check file format.
    if file_metadata["format"] not in FileFormat.get_image_formats():
        return UploadedFileResponse(
            status=FileUploadStatus.FAILED,
            message="Invalid file format for image file: %s." % file_metadata["format"]
        )

    # Create image filename to record.
    file_format = FileFormat(file_metadata["format"])
    unique_filename = generate_unique_filename(file_format=file_format)

    # Save file to disk.
    save_upload_file_to_disk(file=file, unique_filename=unique_filename)

    # Create image file record in the database.
    collection = db.get_collection(name=Collections.FILES.value.name)
    image_file = ImageFile_Create(
        project_id_list=[project_id],
        file_hash=file_hash,
        filename=unique_filename,
        file_format=file_format,
        size_in_bytes=file_metadata["size_in_bytes"],
        width=file_metadata["width"],
        height=file_metadata["height"],
        channels=file_metadata["channels"]
    )
    await collection.insert_one(document=image_file.model_dump())

    # Create response model.
    return UploadedFileResponse(
        status=FileUploadStatus.CREATED,
        message="Image file '%s' uploaded successfully." % file.filename,
        size_in_bytes=file_metadata["size_in_bytes"]
    )

async def create_file_records(
    file_list: UploadFile | list[UploadFile],
    file_processor: callable,
    sync_file_validator: callable,
    sync_get_file_metadata: callable,
    project_id: str,
    db: AsyncDatabase
    ) -> list[dict]:
    """
    Utility function to create file records in the database.

    Args:
        file_list (UploadFile | list[UploadFile]): The upload file or list of upload files to create records for.
        file_processor (callable): The function to process and create the file record.
        project_id (str): The project ID associated with the files.
        db (AsyncDatabase): The database instance.

    Returns:
        list[dict]: List of created file records.
    """
    # Check if single file is provided.
    if isinstance(file_list, UploadFile):
        file_list = [file_list]

    # Process each file.
    processed_file_records = []
    for file in file_list:

        # Get file hash.
        file_hash = await run_in_threadpool(func=get_upload_file_hash, file=file)

        # Check if file already exists.
        existent_file = await get_file_by_it_hash(file_hash=file_hash, db=db)
        if existent_file:

            # Add project ID in project_id_list field of the existing file record.
            await set_project_id_in_file_record(
                file_id=existent_file["_id"],
                project_id=project_id,
                db=db
            )
            file_record = UploadedFileResponse(
                status=FileUploadStatus.SKIPPED,
                message="File '%s' already exists." % file.filename
            )
            processed_file_records.append(file_record.model_dump())
            continue

        # Check file is corrupted.
        is_corrupted = await run_in_threadpool(func=sync_file_validator, file=file)
        if is_corrupted:
            file_record = UploadedFileResponse(
                status=FileUploadStatus.FAILED,
                message="Corrupted file: %s." % file.filename
            )
            processed_file_records.append(file_record.model_dump())
            continue

        # Get file metadata.
        file_metadata = await run_in_threadpool(func=sync_get_file_metadata, file=file)

        # Process file and create record.
        file_record = await file_processor(
            file=file,
            file_metadata=file_metadata,
            project_id=project_id,
            db=db,
            file_hash=file_hash
        )

    return processed_file_records

async def create_image_file_records(
    file_list: UploadFile | list[UploadFile],
    project_id: str,
    db: AsyncDatabase
    ) -> list[dict]:
    """
    Utility function to create image file records in the database.

    Args:
        file_list (UploadFile | list[UploadFile]): The upload file or list of upload files to create records for.
        project_id (str): The project ID associated with the files.
        db (AsyncDatabase): The database instance.

    Returns:
        list[dict]: List of created image file records.
    """
    return await create_file_records(
        file_list=file_list,
        file_processor=process_image_record,
        sync_file_validator=_sync_check_image_corruption,
        sync_get_file_metadata=_sync_get_image_metadata,
        project_id=project_id,
        db=db
    )

async def set_project_id_in_file_record(
    file_id: PyObjectId,
    project_id: PyObjectId,
    db: AsyncDatabase
    ) -> None:
    """
    Utility function to set the project ID in the file record's project_id_list field.

    Args:
        file_id (PyObjectId): The file ID to update.
        project_id (PyObjectId): The project ID to add.
        db (AsyncDatabase): The database instance.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Update file record to add project ID in project_id_list field.
    await collection.update_one(
        filter={"_id": file_id},
        update={"$addToSet": {"project_id_list": project_id}}
    )
