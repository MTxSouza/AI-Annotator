"""
Module with all endpoints related to file operations.
"""
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.params import File, Param, Path
from fastapi.requests import Request
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.files import (AudioFile, ImageFile, TextFile,
                                         UploadedFileListResponse)
from backend.api.v1.models.projects import Project
from backend.api.v1.utils.files import (create_image_file_records,
                                        create_text_file_records, get_files)
from backend.api.v1.utils.projects import get_authenticated_project
from backend.database.configs import DatabaseConfig
from backend.limiter import limiter

# Instantiate the router.
router = APIRouter(
    prefix="/files",
    tags=["Files"],
    dependencies=[Depends(dependency=DatabaseConfig.get_database)]
)

# Endpoints.
@router.get(path="/", response_model=list[ImageFile | TextFile | AudioFile], status_code=status.HTTP_200_OK)
async def get_files_endpoint(
    limit: int = Param(default=10, ge=1, le=100),
    offset: int = Param(default=0, ge=0),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> list[ImageFile | TextFile | AudioFile]:
    """
    Endpoint to get all files.

    Returns:
        list: List of all files.
    """
    return await get_files(limit=limit, offset=offset, db=db)

@router.post(path="/{id}/images/", response_model=UploadedFileListResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_image_file_endpoint(
    request: Request,
    file_list: UploadFile | list[UploadFile] = File(...),
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> UploadedFileListResponse:
    """
    Endpoint to upload an image file.

    Args:
        file_list (UploadFile | list[UploadFile]): The image file or list of image files to upload.

    Returns:
        UploadedFileListResponse: The uploaded image files.
    """
    # Get project ID.
    project_id = project.id

    # Process images.
    data = await create_image_file_records(
        file_list=file_list,
        project_id=project_id,
        db=db
    )
    return UploadedFileListResponse(data=data)

@router.post(path="/{id}/texts/", response_model=UploadedFileListResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_text_file_endpoint(
    request: Request,
    file_list: UploadFile | list[UploadFile] = File(...),
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> UploadedFileListResponse:
    """
    Endpoint to upload a text file.

    Args:
        file_list (list[UploadFile]): The list of text files to upload.

    Returns:
        UploadedFileListResponse: The uploaded text files.
    """
    # Get project ID.
    project_id = project.id

    # Process texts.
    data = await create_text_file_records(
        file_list=file_list,
        project_id=project_id,
        db=db
    )
    return UploadedFileListResponse(data=data)

@router.post(path="/{id}/audios/", response_model=UploadedFileListResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_audio_file_endpoint(
    request: Request,
    file_list: list[UploadFile] = File(...),
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> UploadedFileListResponse:
    """
    Endpoint to upload an audio file.

    Args:
        file_list (list[UploadFile]): The list of audio files to upload.

    Returns:
        UploadedFileListResponse: The uploaded audio files.
    """
    # NOT IMPLEMENTED YET.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Audio file upload not implemented yet.")
