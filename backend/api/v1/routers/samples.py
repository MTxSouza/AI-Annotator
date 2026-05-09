"""
Module with all endpoints related to sample operations.
"""

from fastapi import APIRouter, Depends, status
from fastapi.params import Param
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.projects import Project
from backend.api.v1.models.samples import AudioTranscriptionSample, ObjectDetectionSample, TextClassificationSample
from backend.api.v1.utils.projects import get_authenticated_project
from backend.api.v1.utils.samples import (
    _SAMPLE_CREATE_,
    _SAMPLE_UPDATE_,
    create_sample,
    delete_sample,
    get_sample_by_id,
    get_samples,
    update_sample,
)
from backend.database.configs import DatabaseConfig

# Instantiate the router.
router = APIRouter(
    prefix="/projects/{project_id}/samples",
    tags=["Samples"],
    dependencies=[Depends(dependency=DatabaseConfig.get_database), Depends(dependency=get_authenticated_project)],
)


# Sample responses.
__SAMPLE_RESPONSES__ = TextClassificationSample | ObjectDetectionSample | AudioTranscriptionSample


# Endpoints.
@router.get(path="/", response_model=list[__SAMPLE_RESPONSES__], status_code=status.HTTP_200_OK)
async def get_samples_endpoint(
    limit: int = Param(default=10, ge=1, le=1000),  # type: ignore
    offset: int = Param(default=0, ge=0),  # type: ignore
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> list[__SAMPLE_RESPONSES__]:
    """
    Endpoint to get all samples of a project.

    Returns:
            list: List of all samples.
    """
    # Get project ID.
    project_id = project.id

    return await get_samples(limit=limit, offset=offset, db=db, query={"project_id": project_id})  # type: ignore


@router.get(path="/{sample_id}", response_model=__SAMPLE_RESPONSES__, status_code=status.HTTP_200_OK)
async def get_sample_endpoint(
    sample_id: str,
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> __SAMPLE_RESPONSES__:
    """
    Endpoint to get a sample by ID.

    Returns:
            __SAMPLE_RESPONSES__: The sample with the specified ID.
    """
    return await get_sample_by_id(sample_id=sample_id, db=db)  # type: ignore


@router.post(path="/", response_model=__SAMPLE_RESPONSES__, status_code=status.HTTP_201_CREATED)
async def create_sample_endpoint(
    sample: _SAMPLE_CREATE_,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> __SAMPLE_RESPONSES__:
    """
    Endpoint to create a new sample.

    Args:
            sample (_SAMPLE_CREATE_): The sample data to create.

    Returns:
            __SAMPLE_RESPONSES__: The created sample.
    """
    return await create_sample(sample_data=sample, db=db)  # type: ignore


@router.put(path="/{sample_id}", response_model=__SAMPLE_RESPONSES__, status_code=status.HTTP_200_OK)
async def update_sample_endpoint(
    sample_id: str,
    sample: _SAMPLE_UPDATE_,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> __SAMPLE_RESPONSES__:
    """
    Endpoint to update a sample.

    Args:
            id (str): The ID of the project that contains the sample to update.
            sample_id (str): The ID of the sample to update.
            sample (_SAMPLE_UPDATE_): The sample data to update.

    Returns:
            __SAMPLE_RESPONSES__: The updated sample.
    """
    # Get project ID.
    project_id = project.id

    return await update_sample(sample_id=sample_id, project_id=project_id, sample_data=sample, db=db)  # type: ignore


@router.delete(path="/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample_endpoint(
    sample_id: str,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> None:
    """
    Endpoint to delete a sample by ID.

    Args:
            sample_id (str): The ID of the sample to delete.
    """
    # Get project ID.
    project_id = project.id

    await delete_sample(sample_id=sample_id, project_id=project_id, db=db)
