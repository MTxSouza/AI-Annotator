"""
Module with all endpoints related to sample operations.
"""

from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.samples import ObjectDetectionSample
from backend.api.v1.utils.samples import get_samples
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
