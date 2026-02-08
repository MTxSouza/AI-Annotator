"""
Module with all utilities related to sample operations.
"""

from fastapi import status
from fastapi.exceptions import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.samples import ObjectDetectionSample_Create
from backend.database.configs import Collections
from backend.database.enums import PyObjectId


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


async def create_sample(
    sample_data: dict | ObjectDetectionSample_Create, project_id: str | PyObjectId, db: AsyncDatabase
) -> dict:
    """
    Create a new sample in the database.

    Args:
            sample_data (dict | ObjectDetectionSample_Create): The data for the new sample.
            project_id (str | PyObjectId): The ID of the associated project.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The created sample with its ID.
    """
    # Get sample, file and task config collections.
    sample_collection = db.get_collection(name=Collections.SAMPLES.value.name)
    file_collection = db.get_collection(name=Collections.FILES.value.name)
    task_config_collection = db.get_collection(name=Collections.TASK_CONFIGS.value.name)

    # Convert sample_data to dict.
    if isinstance(sample_data, ObjectDetectionSample_Create):
        sample_data_dict = sample_data.model_dump()
    else:
        sample_data_dict = sample_data

    # Check if associated file exists.
    file_id = sample_data_dict.get("file_id")
    file_id_obj = PyObjectId(oid=file_id)
    file = await file_collection.find_one({"_id": file_id_obj})
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File with ID {file_id} does not exist.")

    # Check if file belongs to the specified project.
    project_id_obj = PyObjectId(oid=project_id)
    if project_id_obj not in file.get("project_id_list", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File with ID {file_id} does not belong to project with ID {project_id}.",
        )

    # Create sample document.
    sample_data_dict["project_id"] = project_id_obj
    result = await sample_collection.insert_one(sample_data_dict)

    # Add new class name to project if it doesn't exist.
    class_name = sample_data_dict.get("class_name")
    await task_config_collection.update_one(
        {"project_id": project_id_obj}, {"$addToSet": {"class_name_list": class_name}}
    )

    # Retrieve the created sample.
    created_sample = await sample_collection.find_one({"_id": result.inserted_id})

    return created_sample  # type: ignore
