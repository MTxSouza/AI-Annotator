"""
Module with all utilities related to sample operations.
"""

from fastapi import status
from fastapi.exceptions import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.samples import ObjectDetectionSampleCreate
from backend.database.configs import Collections
from backend.database.enums import PyObjectId, Task


# Functions.
async def get_samples(limit: int, offset: int, db: AsyncDatabase) -> list[dict]:
    """
    Get all samples.

    Args:
            limit (int): The maximum number of samples to return.
            offset (int): The number of samples to skip before starting to collect the result set.
            db (AsyncDatabase): The database instance.

    Returns:
            list: List of all samples.
    """
    # Get samples collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Query samples.
    cursor = collection.find().skip(skip=offset).limit(limit=limit)
    samples = await cursor.to_list()

    return samples


async def get_sample_by_id(sample_id: str, db: AsyncDatabase) -> dict | None:
    """
    Get a sample by its ID.

    Args:
            sample_id (str): The ID of the sample to retrieve.
            db (AsyncDatabase): The database instance.

    Returns:
            dict | None: The sample with the specified ID or None if not found.
    """
    # Get samples collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Query sample by ID.
    sample = await collection.find_one({"_id": sample_id})

    return sample


async def get_create_sample_metadata(
    sample_data: dict | ObjectDetectionSampleCreate, project_id: str | PyObjectId, db: AsyncDatabase
) -> dict:
    """
    Get the metadata for creating a sample.

    Args:
            sample_data (dict | ObjectDetectionSampleCreate): The data for the new sample.
            project_id (str | PyObjectId): The ID of the associated project.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The metadata for creating the sample.
    """
    # Get file and project collections.
    file_collection = db.get_collection(name=Collections.FILES.value.name)
    project_collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Convert sample_data to dict.
    if not isinstance(sample_data, dict):
        sample_data_dict = sample_data.model_dump()
    else:
        sample_data_dict = sample_data

    # Check if associated file exists and get its metadata.
    file_id = sample_data_dict.get("file_id")
    file_id_obj = PyObjectId(oid=file_id)
    file = await file_collection.find_one({"_id": file_id_obj})
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File with ID {file_id} does not exist.")

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
    }


async def _object_detection_sample_setup(created_sample: dict, project_id: str | PyObjectId, db: AsyncDatabase) -> None:
    """
    Setup extra configurations for an object detection sample.

    Args:
            created_sample (dict): The created sample.
            project_id (str | PyObjectId): The ID of the associated project.
            db (AsyncDatabase): The database instance.
    """
    # Get task config collection.
    collection = db.get_collection(name=Collections.TASK_CONFIGS.value.name)

    # Add new class name to project if it doesn't exist.
    class_name = created_sample.get("class_name")
    project_id_obj = PyObjectId(oid=project_id)
    await collection.update_one({"project_id": project_id_obj}, {"$addToSet": {"class_name_list": class_name}})


async def create_sample(
    sample_data: dict | ObjectDetectionSampleCreate, project_id: str | PyObjectId, db: AsyncDatabase
) -> dict:
    """
    Create a new sample in the database.

    Args:
            sample_data (dict | ObjectDetectionSampleCreate): The data for the new sample.
            project_id (str | PyObjectId): The ID of the associated project.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The created sample with its ID.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Convert sample_data to dict.
    if not isinstance(sample_data, dict):
        sample_data_dict = sample_data.model_dump()
    else:
        sample_data_dict = sample_data

    # Get sample metadata.
    metadata = await get_create_sample_metadata(sample_data=sample_data, project_id=project_id, db=db)

    # Check project task.
    task_map = {Task.OBJECT_DETECTION.value: _object_detection_sample_setup}
    task: str = metadata.get("task")  # type: ignore
    sample_setup = task_map.get(task)
    if not sample_setup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported task: {task}.")

    # Create sample document.
    project_id_obj = PyObjectId(oid=project_id)
    sample_data_dict["project_id"] = project_id_obj
    result = await collection.insert_one(sample_data_dict)
    await sample_setup(created_sample=sample_data_dict, project_id=project_id, db=db)

    # Retrieve the created sample.
    created_sample = await collection.find_one({"_id": result.inserted_id})

    return created_sample  # type: ignore
