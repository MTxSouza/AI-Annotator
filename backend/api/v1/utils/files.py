"""
Module with all utilities related to file operations.
"""

import hashlib
import shutil
import struct
import uuid
from collections.abc import Callable, Generator
from pathlib import Path

import soundfile as sf
from fastapi import UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.files import AudioFileCreate, ImageFileCreate, TextFileCreate, UploadedFileResponse
from backend.api.v1.utils.common import _load_file_content
from backend.api.v1.utils.samples import delete_samples_by_file_id
from backend.api.v1.utils.task_details import get_task_file
from backend.configs import BackendSettings
from backend.database.configs import Collections
from backend.database.enums import FileFormat, FileUploadStatus, PyObjectId

# Global variables.
FILE_CHUNK_SIZE = 64 * 1024  # 64 KB
FILE_FORMAT_CHUNK_SIZE = 512  # 512 Bytes


# Functions.
async def check_if_file_belongs_to_project(
    file_id: str | PyObjectId, project_id: str | PyObjectId, db: AsyncDatabase
) -> None:
    """
    Check if a file belongs to a project.

    Args:
            file_id (str | PyObjectId): The ID of the file.
            project_id (str | PyObjectId): The ID of the project.
            db (AsyncDatabase): The database instance.
    """
    # Query file by ID.
    file = await get_file_by_id(file_id=file_id, db=db)
    file_project_id_list = file.get("project_id_list", [])
    file_project_id_list = [PyObjectId(oid=pid) for pid in file_project_id_list]  # type: ignore

    # Check if file belongs to the specified project.
    project_id_obj = PyObjectId(oid=project_id)
    if file_project_id_list and project_id_obj not in file_project_id_list:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} does not belong to project with ID {project_id}.",
        )


def generate_unique_filename(file_format: FileFormat) -> str:
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
    unique_filename = f"{unique_id}.{file_extension}"
    return unique_filename


def load_upload_file_in_chunks(file: UploadFile) -> Generator[bytes, None, None]:
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


def get_upload_file_hash(file: UploadFile) -> str:
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


def get_file_metadata(file: UploadFile) -> dict:
    """
    Utility function to get metadata of an upload file.

    Args:
            file (UploadFile): The upload file to get metadata for.

    Returns:
            dict: Metadata of the upload file.
    """
    # Get file extension.
    file_size = file.size
    file_extension = file.content_type.split(sep="/")[-1].lower()  # type: ignore
    return {"format": file_extension, "size_in_bytes": file_size}


def save_upload_file_to_disk(file: UploadFile, unique_filename: str) -> None:
    """
    Utility function to save the upload file to disk.

    Args:
            file (UploadFile): The upload file to save.
            unique_filename (str): The unique filename to save the file as.
    """
    # Move cursor to the beginning of the file.
    file.file.seek(0)

    # Save file in chunks to avoid memory issues.
    with Path(BackendSettings.static_file_directory, unique_filename).open(mode="wb") as file_buffer:
        shutil.copyfileobj(fsrc=file.file, fdst=file_buffer)


def save_temporary_upload_file_to_disk(file: UploadFile) -> str:
    """
    Utility function to save the upload file to disk with a temporary filename.

    Args:
            file (UploadFile): The upload file to save.

    Returns:
            str: The temporary filename the file was saved as.
    """
    # Generate a unique temporary filename.
    temp_filename = f"temp_{uuid.uuid4()}"

    # Save file to disk.
    save_upload_file_to_disk(file=file, unique_filename=temp_filename)

    return temp_filename


async def get_files(limit: int, offset: int, db: AsyncDatabase, query: dict | None = None) -> list[dict]:
    """
    Utility function to get all files from the database.

    Args:
            limit (int): The maximum number of files to retrieve.
            offset (int): The number of files to skip.
            db (AsyncDatabase): The database instance.
            query (dict): The query to filter files. (Default: None)

    Returns:
            list[dict]: List of all files.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Setup query.
    if query is None:
        query = {}

    # Query files.
    cursor = collection.find(query).skip(offset).limit(limit)
    files = await cursor.to_list()

    return files


async def get_file_by_id(file_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Utility function to get a file from the database by its ID.

    Args:
            file_id (str | PyObjectId): The ID of the file to retrieve.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The file document.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Query file by its ID.
    file_id_obj = PyObjectId(oid=file_id)
    file_document = await collection.find_one({"_id": file_id_obj})
    if not file_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File with ID {file_id} does not exist.")

    return file_document


async def get_file_by_it_hash(file_hash: str, db: AsyncDatabase) -> dict | None:
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


async def load_file_content_by_id(
    file_id: str | PyObjectId, project_id: str | PyObjectId, db: AsyncDatabase
) -> Response:
    """
    Utility function to load the content of a file from disk by its ID.

    Args:
            file_id (str | PyObjectId): The ID of the file to load.
            project_id (str | PyObjectId): The ID of the project the file belongs to.
            db (AsyncDatabase): The database instance.

    Returns:
            Response: The response containing the file content and metadata.
    """
    # Check if file belongs to the project.
    await check_if_file_belongs_to_project(file_id=file_id, project_id=project_id, db=db)

    # Get file document.
    file_document = await get_file_by_id(file_id=file_id, db=db)
    filename = file_document["filename"]
    file_format = file_document["file_format"]

    # Set media type based on file format.
    media_type_map = {
        FileFormat.JPEG.value: "image/jpeg",
        FileFormat.PNG.value: "image/png",
        FileFormat.TXT.value: "text/plain",
        FileFormat.WAV.value: "audio/wav",
        FileFormat.MP3.value: "audio/mpeg",
    }
    media_type = media_type_map.get(file_format)  # type: ignore
    if not media_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file format: {file_format}.")  # type: ignore

    # Load file content and format.
    content = await run_in_threadpool(func=_load_file_content, filename=filename, file_id=file_id)

    # Create response.
    return Response(content=content, media_type=media_type)  # type: ignore


async def is_file_exists(file: UploadFile, db: AsyncDatabase) -> bool:
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


def _sync_get_file_format(file: UploadFile) -> FileFormat | None:
    """
    Utility function to get the file format of an upload file.

    Args:
            file (UploadFile): The upload file to get the format for.

    Returns:
            FileFormat | None: The file format if detected, None otherwise.
    """
    # Move cursor to the beginning of the file.
    file.file.seek(0)

    # Load file bytes.
    file_bytes = file.file.read(FILE_FORMAT_CHUNK_SIZE)

    # Check file format.
    return FileFormat._check_file_format(file_bytes=file_bytes)


def _sync_check_image_corruption(file: UploadFile) -> bool:
    """
    Synchronous utility function to check if an image file is corrupted.

    Args:
            file (UploadFile): The upload file to check.

    Returns:
            bool: True if the image file is corrupted, False otherwise.
    """
    try:
        file.file.seek(0)
        with Image.open(fp=file.file) as img_buffer:
            img_buffer.verify()
        return False
    except (UnidentifiedImageError, OSError):
        return True


def _sync_check_text_corruption(file: UploadFile) -> bool:
    """
    Synchronous utility function to check if a text file is corrupted.

    Args:
            file (UploadFile): The upload file to check.

    Returns:
            bool: True if the text file is corrupted, False otherwise.
    """
    try:
        file.file.seek(0)

        # Load file bytes.
        file_bytes = file.file.read(FILE_FORMAT_CHUNK_SIZE)

        # Check if the file bytes can be decoded as UTF-8.
        if not FileFormat.is_utf8_text(file_bytes=file_bytes):
            return True

    except Exception:
        return True

    finally:
        file.file.seek(0)

    return False


def _sync_check_audio_corruption(file: UploadFile) -> bool:
    """
    Synchronous utility function to check if an audio file is corrupted.

    Args:
            file (UploadFile): The upload file to check.

    Returns:
            bool: True if the audio file is corrupted, False otherwise.
    """
    try:
        # Get real audio size.
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        # Check header of the file.
        audio_header_signature = file.file.read(4)
        if audio_header_signature == b"RIFF":  # WAV file header signature.
            # Check declared file size in header.
            chunk_size_bytes = file.file.read(4)
            if len(chunk_size_bytes) < 4:
                return True

            declared_file_size = (
                struct.unpack("<I", chunk_size_bytes)[0] + 8
            )  # Chunk size does not include the header size (8 bytes).
            if declared_file_size > file_size:
                return True

        # Load file bytes.
        file.file.seek(0)
        with sf.SoundFile(file=file.file) as file_buffer:
            # Check if audio has no frames.
            if not file_buffer.frames:
                return True

            # Check if audio has lower sample rate.
            if file_buffer.samplerate < 8000:
                return True

            # Truncate file buffer to the end of the file to check for any read errors.
            seek_position = max(0, file_buffer.frames - FILE_FORMAT_CHUNK_SIZE)
            file_buffer.seek(seek_position)

            audio_data = file_buffer.read(dtype="float32")
            if not audio_data.shape[0] and file_buffer.frames > 0:
                return True

    except Exception:
        return True

    finally:
        file.file.seek(0)

    return False


def _sync_get_image_metadata(file: UploadFile) -> dict:
    """
    Synchronous utility function to get metadata of an image upload file.

    Args:
            file (UploadFile): The upload file to get metadata for.

    Returns:
            dict: Metadata of the upload file.
    """
    # Get file size.
    file_size = file.size

    # Get image dimensions.
    file.file.seek(0)
    with Image.open(fp=file.file) as img_buffer:
        width, height = img_buffer.size
        channels = len(img_buffer.getbands())

    return {"size_in_bytes": file_size, "width": width, "height": height, "channels": channels}


def _sync_get_text_metadata(file: UploadFile) -> dict:
    """
    Synchronous utility function to get metadata of a text upload file.

    Args:
            file (UploadFile): The upload file to get metadata for.

    Returns:
            dict: Metadata of the upload file.
    """
    # Get file size.
    file_size = file.size

    # Check number of lines, words and characters.
    file.file.seek(0)
    number_of_lines = 0
    number_of_words = 0
    number_of_characters = 0
    for line in file.file:
        decoded_line = line.decode(encoding="utf-8", errors="ignore")
        number_of_lines += 1
        number_of_words += len(decoded_line.split())
        number_of_characters += len(decoded_line)

    return {
        "size_in_bytes": file_size,
        "number_of_lines": number_of_lines,
        "number_of_words": number_of_words,
        "number_of_characters": number_of_characters,
    }


def _sync_get_audio_metadata(file: UploadFile) -> dict:
    """
    Synchronous utility function to get metadata of an audio upload file.

    Args:
            file (UploadFile): The upload file to get metadata for.

    Returns:
            dict: Metadata of the upload file.
    """
    # Get file size.
    file_size = file.size

    # Get audio properties.
    file.file.seek(0)
    with sf.SoundFile(file=file.file) as file_buffer:
        sample_rate = file_buffer.samplerate
        channels = file_buffer.channels
        duration_in_seconds = file_buffer.frames / sample_rate if sample_rate else 0

    return {
        "size_in_bytes": file_size,
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_in_seconds": duration_in_seconds,
    }


def _is_valid_image_file_format(file_format: FileFormat) -> bool:
    """
    Utility function to check if a file format is a valid image file format.

    Args:
            file_format (FileFormat): The file format to check.

    Returns:
            bool: True if the file format is a valid image file format, False otherwise.
    """
    return file_format in FileFormat.get_image_formats()


def _is_valid_text_file_format(file_format: FileFormat) -> bool:
    """
    Utility function to check if a file format is a valid text file format.

    Args:
            file_format (FileFormat): The file format to check.

    Returns:
            bool: True if the file format is a valid text file format, False otherwise.
    """
    return file_format in FileFormat.get_text_formats()


def _is_valid_audio_file_format(file_format: FileFormat) -> bool:
    """
    Utility function to check if a file format is a valid audio file format.

    Args:
            file_format (FileFormat): The file format to check.

    Returns:
            bool: True if the file format is a valid audio file format, False otherwise.
    """
    return file_format in FileFormat.get_audio_formats()


async def process_file_record(
    file_type_name: str,
    file: UploadFile,
    file_metadata: dict,
    file_hash: str,
    project_id: str | PyObjectId,
    db: AsyncDatabase,
    create_model_schema: BaseModel,
) -> UploadedFileResponse:
    """
    Utility function to process a file and create its record in the database.

    Args:
            file_type_name (str): The name of the file type to process (for logging purposes).
            file (UploadFile): The upload file to process.
            file_metadata (dict): The metadata of the upload file.
            file_hash (str): The hash of the upload file.
            project_id (str | PyObjectId): The project ID associated with the file.
            db (AsyncDatabase): The database instance.
            create_model_schema (BaseModel): The Pydantic model schema to use for creating the file record.

    Returns:
            UploadedFileResponse: The response model for the uploaded file.
    """
    # Setup project ID object.
    project_id_obj = PyObjectId(oid=project_id)

    # Create filename to record.
    file_metadata["file_format"] = FileFormat(file_metadata["file_format"])
    unique_filename = generate_unique_filename(file_format=file_metadata["file_format"])

    # Save file to disk.
    save_upload_file_to_disk(file=file, unique_filename=unique_filename)

    # Create file record in the database.
    collection = db.get_collection(name=Collections.FILES.value.name)
    file_schema = create_model_schema(  # type: ignore
        project_id_list=[project_id_obj],
        file_hash=file_hash,
        filename=unique_filename,
        **file_metadata,
    ).model_dump()
    result = await collection.insert_one(document=file_schema)

    # Create response model.
    return UploadedFileResponse(
        file_id=result.inserted_id,
        status=FileUploadStatus.CREATED,
        message=f"{file_type_name.title()} file '{file.filename}' uploaded successfully.",
        size_in_bytes=file_schema["size_in_bytes"],
    )


async def create_file_records(
    file_list: UploadFile | list[UploadFile],
    project_id: str | PyObjectId,
    db: AsyncDatabase,
) -> list[dict]:
    """
    Utility function to create file records in the database.

    Args:
            file_list (UploadFile | list[UploadFile]): The upload file or list of upload files to create records for.
            project_id (str | PyObjectId): The project ID associated with the files.
            db (AsyncDatabase): The database instance.

    Returns:
            list[dict]: List of created file records.
    """
    # Check if single file is provided.
    if isinstance(file_list, UploadFile):
        file_list = [file_list]

    # Get project task.
    project_collection = db.get_collection(name=Collections.PROJECTS.value.name)
    task: dict = await project_collection.find_one({"_id": PyObjectId(oid=project_id)}, {"task": 1})  # type: ignore
    task_name: str = task.get("task")  # type: ignore

    # Get task-file utility mapping.
    file_type = get_task_file(task=task_name)
    if not file_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported task: {task_name}.")

    task_map = {
        "image": {
            "file_type_name": "image",
            "create_model_schema": ImageFileCreate,
            "is_valid_file_format": _is_valid_image_file_format,
            "sync_file_validator": _sync_check_image_corruption,
            "sync_get_file_metadata": _sync_get_image_metadata,
        },
        "text": {
            "file_type_name": "text",
            "create_model_schema": TextFileCreate,
            "is_valid_file_format": _is_valid_text_file_format,
            "sync_file_validator": _sync_check_text_corruption,
            "sync_get_file_metadata": _sync_get_text_metadata,
        },
        "audio": {
            "file_type_name": "audio",
            "create_model_schema": AudioFileCreate,
            "is_valid_file_format": _is_valid_audio_file_format,
            "sync_file_validator": _sync_check_audio_corruption,
            "sync_get_file_metadata": _sync_get_audio_metadata,
        },
    }
    task_utils = task_map.get(file_type)
    if not task_utils:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {file_type}.")

    file_type_name: str = task_utils["file_type_name"]  # type: ignore
    create_model_schema: BaseModel = task_utils["create_model_schema"]  # type: ignore
    is_valid_file_format: Callable = task_utils["is_valid_file_format"]  # type: ignore
    sync_file_validator: Callable = task_utils["sync_file_validator"]  # type: ignore
    sync_get_file_metadata: Callable = task_utils["sync_get_file_metadata"]  # type: ignore

    # Process each file.
    processed_file_records = []
    for file in file_list:
        # Get file hash.
        file_hash = await run_in_threadpool(func=get_upload_file_hash, file=file)

        # Check if file already exists.
        existent_file = await get_file_by_it_hash(file_hash=file_hash, db=db)
        if existent_file:
            # Add project ID in project_id_list field of the existing file record.
            await set_project_id_in_file_record(file_id=existent_file["_id"], project_id=project_id, db=db)
            file_record = UploadedFileResponse(
                status=FileUploadStatus.SKIPPED, message=f"File '{file.filename}' already exists."
            )
            processed_file_records.append(file_record.model_dump())
            continue

        # Check file format.
        file_format = await run_in_threadpool(
            func=_sync_get_file_format, file=file
        )  # Common function to get file format.
        if file_format is None:
            file_record = UploadedFileResponse(
                status=FileUploadStatus.FAILED,
                message=f"Invalid file format: {file.content_type}. This file format is not supported at all.",
            )
            processed_file_records.append(file_record.model_dump())
            continue

        if not is_valid_file_format(file_format=file_format):
            file_record = UploadedFileResponse(
                status=FileUploadStatus.FAILED, message=f"Invalid file format for this project: {file_format.value}."
            )
            processed_file_records.append(file_record.model_dump())
            continue

        # Check file is corrupted.
        is_corrupted = await run_in_threadpool(func=sync_file_validator, file=file)
        if is_corrupted:
            file_record = UploadedFileResponse(
                status=FileUploadStatus.FAILED, message=f"Corrupted file: {file.filename}."
            )
            processed_file_records.append(file_record.model_dump())
            continue

        # Get file metadata.
        file_metadata = await run_in_threadpool(func=sync_get_file_metadata, file=file)
        file_metadata["file_format"] = file_format.value  # Ensure format is consistent.

        # Process file and create record.
        file_record = await process_file_record(
            file_type_name=file_type_name,
            file=file,
            file_metadata=file_metadata,
            project_id=project_id,
            db=db,
            file_hash=file_hash,
            create_model_schema=create_model_schema,
        )
        processed_file_records.append(file_record.model_dump())

    return processed_file_records


async def set_project_id_in_file_record(
    file_id: str | PyObjectId, project_id: str | PyObjectId, db: AsyncDatabase
) -> None:
    """
    Utility function to set the project ID in the file record's project_id_list field.

    Args:
            file_id (str | PyObjectId): The file ID to update.
            project_id (str | PyObjectId): The project ID to add.
            db (AsyncDatabase): The database instance.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Fix file ID type.
    if isinstance(file_id, str):
        file_id_obj = PyObjectId(oid=file_id)
    else:
        file_id_obj = file_id

    # Fix project ID type.
    if isinstance(project_id, str):
        project_id_obj = PyObjectId(oid=project_id)
    else:
        project_id_obj = project_id

    # Update file record to add project ID in project_id_list field.
    await collection.update_one(filter={"_id": file_id_obj}, update={"$addToSet": {"project_id_list": project_id_obj}})


async def unset_project_id_in_file_records(project_id: str | PyObjectId, db: AsyncDatabase) -> None:
    """
    Utility function to unset the project ID from all file record's project_id_list field.

    Args:
            project_id (str | PyObjectId): The project ID to remove from file records.
            db (AsyncDatabase): The database instance.
    """
    # Get files collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Get all files that belong to the project.
    project_id_obj = PyObjectId(oid=project_id)
    file_id_list = await collection.distinct(key="_id", filter={"project_id_list": {"$in": [project_id_obj]}})

    # Delete files that no longer belong to any project.
    if file_id_list:
        await delete_file_records(file_id=file_id_list, project_id=project_id_obj, db=db)


async def delete_file_records(
    file_id: str | PyObjectId | list[str] | list[PyObjectId], project_id: str | PyObjectId, db: AsyncDatabase
) -> None:
    """
    Utility function to delete file records from a project.

    Args:
            file_id (str | PyObjectId | list[str] | list[PyObjectId]): The file ID(s) to delete.
            project_id (str | PyObjectId): The project ID to remove the file from.
            db (AsyncDatabase): The database instance.
    """
    # Get file collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Check if file_id is a list.
    if isinstance(file_id, list):
        file_id_obj_list = [PyObjectId(oid=fid) for fid in file_id]
    else:
        file_id_obj_list = [PyObjectId(oid=file_id)]

    # Check if file belongs to the project.
    for fid in file_id_obj_list:
        await check_if_file_belongs_to_project(file_id=fid, project_id=project_id, db=db)

    # Delete associated samples.
    await delete_samples_by_file_id(file_id=file_id_obj_list, db=db, project_id=project_id)

    # Update all file records to remove the project ID from their project_id_list field.
    project_id_obj = PyObjectId(oid=project_id)
    await collection.update_many(
        filter={"_id": {"$in": file_id_obj_list}}, update={"$pull": {"project_id_list": project_id_obj}}
    )

    # Get all files that no longer belong to any project and delete them from the database and disk.
    orphan_file_id_list = await collection.distinct(key="_id", filter={"project_id_list": {"$size": 0}})
    if orphan_file_id_list:
        # Delete files from disk.
        filename_list = await collection.distinct(key="filename", filter={"_id": {"$in": orphan_file_id_list}})
        for filename in filename_list:
            file_path = Path(BackendSettings.static_file_directory, filename)
            file_path.unlink(missing_ok=True)

        # Delete file records from the database.
        await collection.delete_many({"_id": {"$in": orphan_file_id_list}})
