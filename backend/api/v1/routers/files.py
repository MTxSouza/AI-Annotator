"""
Module with all endpoints related to file operations.
"""

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.params import File, Param
from fastapi.requests import Request
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.files import AudioFile, ImageFile, TextFile, UploadedFileListResponse
from backend.api.v1.models.projects import Project
from backend.api.v1.utils.files import create_file_records, get_files
from backend.api.v1.utils.projects import get_authenticated_project
from backend.database.configs import DatabaseConfig
from backend.limiter import limiter

# Instantiate the router.
router = APIRouter(prefix="/files", tags=["Files"], dependencies=[Depends(dependency=DatabaseConfig.get_database)])


# Endpoints.
@router.get(path="/", response_model=list[ImageFile | TextFile | AudioFile], status_code=status.HTTP_200_OK)
async def get_files_endpoint(
    limit: int = Param(default=10, ge=1, le=100),  # type: ignore
    offset: int = Param(default=0, ge=0),  # type: ignore
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> list[ImageFile | TextFile | AudioFile]:
    """
    Endpoint to get all files.

    Returns:
            list: List of all files.
    """
    return await get_files(limit=limit, offset=offset, db=db)  # type: ignore


@router.post(path="/{id}/", response_model=UploadedFileListResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_file_endpoint(
    request: Request,
    file_list: UploadFile | list[UploadFile] = File(...),  # type: ignore
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> UploadedFileListResponse:
    """
    Endpoint to upload any file. This endpoint will automatically check the project task and validate
    the correct file type.

    Args:
            file_list (UploadFile | list[UploadFile]): The file or list of files to upload.

    Returns:
            UploadedFileListResponse: The uploaded files.
    """
    # Get project ID.
    project_id = project.id

    # Process files.
    data = await create_file_records(file_list=file_list, project_id=project_id, db=db)
    return UploadedFileListResponse(data=data)  # type: ignore
