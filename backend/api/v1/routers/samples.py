"""
Module with all endpoints related to sample operations.
"""

from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.projects import Project
from backend.api.v1.models.samples import (
    ObjectDetectionSample,
    ObjectDetectionSampleCreate,
    ObjectDetectionSampleUpdate,
)
from backend.api.v1.utils.projects import get_authenticated_project
from backend.api.v1.utils.samples import create_sample, get_sample_by_id, get_samples, update_sample
from backend.database.configs import DatabaseConfig

# Instantiate the router.
router = APIRouter(prefix="/samples", tags=["Samples"], dependencies=[Depends(dependency=DatabaseConfig.get_database)])


# Endpoints.
@router.get(path="/", response_model=list[ObjectDetectionSample], status_code=status.HTTP_200_OK)
async def get_samples_endpoint(
    limit: int = 10,
    offset: int = 0,
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> list[ObjectDetectionSample]:
    """
    Endpoint to get all samples.

    Returns:
            list: List of all samples.
    """
    return await get_samples(limit=limit, offset=offset, db=db)  # type: ignore


@router.get(path="/{id}", response_model=ObjectDetectionSample, status_code=status.HTTP_200_OK)
async def get_sample_endpoint(
    id: str,
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> ObjectDetectionSample:
    """
    Endpoint to get a sample by ID.

    Returns:
            ObjectDetectionSample: The sample with the specified ID.
    """
    return await get_sample_by_id(sample_id=id, db=db)  # type: ignore


@router.post(path="/{id}/", response_model=ObjectDetectionSample, status_code=status.HTTP_201_CREATED)
async def create_sample_endpoint(
    sample: ObjectDetectionSampleCreate,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> ObjectDetectionSample:
    """
    Endpoint to create a new sample.

    Args:
            sample (ObjectDetectionSampleCreate): The sample data to create.

    Returns:
            ObjectDetectionSample: The created sample.
    """
    # Get project ID.
    project_id = project.id

    return await create_sample(sample_data=sample, project_id=project_id, db=db)  # type: ignore


@router.put(path="/{id}/", response_model=ObjectDetectionSample, status_code=status.HTTP_201_CREATED)
async def update_sample_endpoint(
    id: str,
    sample: ObjectDetectionSampleUpdate,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> ObjectDetectionSample:
    """
    Endpoint to update a sample.

    Args:
            id (str): The ID of the sample to update.
            sample (ObjectDetectionSampleUpdate): The sample data to update.

    Returns:
            ObjectDetectionSample: The updated sample.
    """
    # Get project ID.
    project_id = project.id

    return await update_sample(sample_id=id, sample_data=sample, project_id=project_id, db=db)  # type: ignore
