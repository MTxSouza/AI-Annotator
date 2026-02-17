"""
Module with all utilities related to sample operations.
"""

from fastapi import status
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import HTTPException
from pymongo.asynchronous.collection import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.samples import (
    ObjectDetectionSampleCreate,
    ObjectDetectionSampleUpdate,
    TextClassificationSampleCreate,
    TextClassificationSampleUpdate,
)
from backend.api.v1.utils.common import _load_file_content
from backend.api.v1.utils.task_details import get_valid_number_of_samples_per_file
from backend.database.configs import Collections
from backend.database.enums import FileFormat, PyObjectId

# Sample input and output types.
_SAMPLE_CREATE_ = TextClassificationSampleCreate | ObjectDetectionSampleCreate
_SAMPLE_UPDATE_ = TextClassificationSampleUpdate | ObjectDetectionSampleUpdate


# Functions.
async def check_if_sample_belongs_to_project(
    sample_id: str | PyObjectId, project_id: str | PyObjectId, db: AsyncDatabase
) -> None:
    """
    Check if a sample belongs to a project.

    Args:
            sample_id (str | PyObjectId): The ID of the sample.
            project_id (str | PyObjectId): The ID of the project.
            db (AsyncDatabase): The database instance.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Query sample by ID.
    sample_id_obj = PyObjectId(oid=sample_id)
    sample = await collection.find_one({"_id": sample_id_obj})

    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sample with ID {sample_id} does not exist.")
    sample_project_id = PyObjectId(oid=sample.get("project_id"))

    # Check if sample belongs to the specified project.
    project_id_obj = PyObjectId(oid=project_id)
    if sample_project_id != project_id_obj:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample with ID {sample_id} does not belong to project with ID {project_id}.",
        )


async def get_samples(limit: int, offset: int, db: AsyncDatabase, query: dict | None = None) -> list[dict]:
    """
    Get all samples.

    Args:
            limit (int): The maximum number of samples to return.
            offset (int): The number of samples to skip before starting to collect the result set.
            db (AsyncDatabase): The database instance.
            query (dict | None): The query to filter samples. (Default: None)

    Returns:
            list: List of all samples.
    """
    # Get samples collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Setup query.
    if query is None:
        query = {}

    # Query samples.
    cursor = collection.find(query).skip(skip=offset).limit(limit=limit)
    samples = await cursor.to_list()

    return samples


async def get_sample_by_id(sample_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Get a sample by its ID.

    Args:
            sample_id (str | PyObjectId): The ID of the sample to retrieve.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The sample with the specified ID or None if not found.
    """
    # Get samples collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Query sample by ID.
    sample_id_obj = PyObjectId(oid=sample_id)
    sample = await collection.find_one({"_id": sample_id_obj})
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sample with ID {sample_id} does not exist.")

    return sample


async def get_create_sample_metadata(
    sample_data: _SAMPLE_CREATE_, project_id: str | PyObjectId, db: AsyncDatabase
) -> dict:
    """
    Get the metadata for creating a sample.

    Args:
            sample_data (_SAMPLE_CREATE_): The data for the new sample.
            project_id (str | PyObjectId): The ID of the associated project.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The metadata for creating the sample.
    """
    # Get file and project collections.
    file_collection = db.get_collection(name=Collections.FILES.value.name)
    project_collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Convert sample_data to dict.
    sample_data_dict = sample_data.model_dump()

    # Check if associated file exists and get its metadata.
    file_id = sample_data_dict.get("file_id")
    file_id_obj = PyObjectId(oid=file_id)
    file = await file_collection.find_one({"_id": file_id_obj})
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File with ID {file_id} does not exist.")

    # Get file format and name.
    file_format = file.get("file_format")
    filename = file.get("filename")

    # Check if file belongs to the specified project.
    project_id_obj = PyObjectId(oid=project_id)
    if project_id_obj not in file.get("project_id_list", []):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} does not belong to project with ID {project_id}.",
        )

    # Get project task.
    document: dict = await project_collection.find_one({"_id": project_id_obj}, {"task": 1})  # type: ignore
    task = document.get("task")

    return {
        "project_id": project_id_obj,
        "file_id": file_id_obj,
        "task": task,
        "file_format": file_format,
        "filename": filename,
    }


async def create_sample(sample_data: _SAMPLE_CREATE_, db: AsyncDatabase) -> dict:
    """
    Create a new sample in the database.

    Args:
            sample_data (_SAMPLE_CREATE_): The data for the new sample.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The created sample with its ID.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Convert sample_data to dict.
    sample_data_dict = sample_data.model_dump()

    # Get sample metadata.
    project_id = sample_data_dict.get("project_id")
    metadata = await get_create_sample_metadata(sample_data=sample_data, project_id=project_id, db=db)  # type: ignore

    # Check number of samples already created for the associated file and task.
    file_id = metadata.get("file_id")
    file_id_obj = PyObjectId(oid=file_id)
    task = metadata.get("task")
    valid_number_of_samples = get_valid_number_of_samples_per_file(task=task)  # type: ignore
    if not valid_number_of_samples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task} is not supported.",
        )

    project_id_obj = PyObjectId(oid=project_id)
    number_of_samples = await collection.count_documents(filter={"project_id": project_id_obj, "file_id": file_id_obj})
    if valid_number_of_samples < 0 and number_of_samples >= valid_number_of_samples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of samples for file with ID {file_id} for the task {task} cannot exceed \
{valid_number_of_samples}.",
        )

    # HARDCODED: Copy the text content of the file to the sample if the task is text-related.
    if metadata.get("file_format") in FileFormat.get_text_formats():
        # Load file content.
        filename = metadata.get("filename")
        text_bytes = await run_in_threadpool(_load_file_content, filename=filename, file_id=metadata.get("file_id"))  # type: ignore
        sample_data_dict["text"] = text_bytes.decode(encoding="utf-8")
        del text_bytes

    # Create sample document.
    result = await collection.insert_one(sample_data_dict)

    # Retrieve the created sample.
    created_sample = await collection.find_one({"_id": result.inserted_id})

    return created_sample  # type: ignore


async def update_sample(
    sample_id: str | PyObjectId,
    project_id: str | PyObjectId,
    sample_data: _SAMPLE_UPDATE_,
    db: AsyncDatabase,
) -> dict:
    """
    Update an existing sample in the database.

    Args:
            sample_id (str | PyObjectId): The ID of the sample to update.
            project_id (str | PyObjectId): The ID of the associated project.
            sample_data (_SAMPLE_UPDATE_): The updated data for the sample.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The updated sample.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Check if sample exists.
    await get_sample_by_id(sample_id=sample_id, db=db)

    # Check if sample belongs to the specified project.
    await check_if_sample_belongs_to_project(sample_id=sample_id, project_id=project_id, db=db)

    # Convert sample_data to dict.
    sample_data_dict = sample_data.model_dump(exclude_unset=True, exclude_none=True)

    # Update sample document.
    sample_id_obj = PyObjectId(oid=sample_id)
    updated_sample = await collection.find_one_and_update(
        {"_id": sample_id_obj}, {"$set": sample_data_dict}, return_document=ReturnDocument.AFTER
    )

    return updated_sample  # type: ignore


async def delete_sample(sample_id: str | PyObjectId, project_id: str | PyObjectId, db: AsyncDatabase) -> None:
    """
    Delete a sample from the database.

    Args:
            sample_id (str | PyObjectId): The ID of the sample to delete.
            project_id (str | PyObjectId): The ID of the associated project.
            db (AsyncDatabase): The database instance.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Check if sample exists.
    await get_sample_by_id(sample_id=sample_id, db=db)

    # Check if sample belongs to the specified project.
    await check_if_sample_belongs_to_project(sample_id=sample_id, project_id=project_id, db=db)

    # Delete the sample.
    sample_id_obj = PyObjectId(oid=sample_id)
    await collection.delete_one({"_id": sample_id_obj})


async def delete_samples_by_file_id(
    file_id: str | PyObjectId | list[str] | list[PyObjectId],
    db: AsyncDatabase,
    project_id: str | PyObjectId | None = None,
) -> None:
    """
    Delete samples associated with a file ID. If project_id is provided, it will only delete samples that belong to the
    specified project.

    Args:
            file_id (str | PyObjectId | list[str] | list[PyObjectId]): The ID(s) of the file(s) whose associated samples
            should be deleted.
            db (AsyncDatabase): The database instance.
            project_id (str | PyObjectId): The ID of the associated project. (Default: None)
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Setup project ID object.
    query_dict = {}
    if project_id:
        project_id_obj = PyObjectId(oid=project_id)
        query_dict["project_id"] = project_id_obj

    # Check if file_id is a list.
    if isinstance(file_id, list):
        file_id_obj_list = [PyObjectId(oid=fid) for fid in file_id]
        query_dict["file_id"] = {"$in": file_id_obj_list}  # type: ignore
    else:
        file_id_obj = PyObjectId(oid=file_id)
        query_dict["file_id"] = file_id_obj

    await collection.delete_many(query_dict)


async def delete_samples_by_project_id(project_id: str | PyObjectId, db: AsyncDatabase) -> None:
    """
    Delete samples associated with a project ID.

    Args:
            project_id (str | PyObjectId): The ID of the project whose associated samples should be deleted.
            db (AsyncDatabase): The database instance.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Delete samples with the specified project ID.
    project_id_obj = PyObjectId(oid=project_id)
    await collection.delete_many({"project_id": project_id_obj})
