"""
Module with all endpoints related to file operations.
"""

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.params import File, Param
from fastapi.requests import Request
from fastapi.responses import Response
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.files import AudioFile, ImageFile, TextFile, UploadedFileListResponse
from backend.api.v1.models.projects import Project
from backend.api.v1.models.worker_tasks import WorkerTaskResult
from backend.api.v1.utils.files import (
    delete_file_records,
    get_files,
    load_file_content_by_id,
    push_upload_file_to_redis_queue,
)
from backend.api.v1.utils.projects import get_authenticated_project
from backend.database.configs import DatabaseConfig
from backend.limiter import limiter

# Instantiate the router.
router = APIRouter(
    prefix="/projects/{project_id}/files",
    tags=["Files"],
    dependencies=[Depends(dependency=DatabaseConfig.get_database), Depends(dependency=get_authenticated_project)],
)


# Endpoints.
@router.get(path="/", response_model=list[ImageFile | TextFile | AudioFile], status_code=status.HTTP_200_OK)
async def get_files_endpoint(
    limit: int = Param(default=10, ge=1, le=100),  # type: ignore
    offset: int = Param(default=0, ge=0),  # type: ignore
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> list[ImageFile | TextFile | AudioFile]:
    """
    Endpoint to get all files of a project.

    Returns:
            list: List of all files.
    """
    # Get project ID.
    project_id = project.id

    return await get_files(limit=limit, offset=offset, db=db, query={"project_id_list": project_id})  # type: ignore


@router.get(path="/{file_id}/data", response_class=Response, status_code=status.HTTP_200_OK)
async def get_file_data_endpoint(
    file_id: str,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> Response:
    """
    Endpoint to get the data of a file by its ID.

    Args:
            file_id (str): The ID of the file to get.

    Returns:
            Response: The file data.
    """
    # Get project ID.
    project_id = project.id

    return await load_file_content_by_id(file_id=file_id, project_id=project_id, db=db)  # type: ignore


@router.post(path="/", response_model=UploadedFileListResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
@limiter.limit("10/minute")
async def _upload_file_endpoint(
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
    raise HTTPException(
        status_code=status.HTTP_410_GONE, detail="This endpoint is deprecated. Please use the /queue endpoint instead."
    )


@router.post(path="/queue", response_model=WorkerTaskResult, status_code=status.HTTP_202_ACCEPTED)
async def upload_file_endpoint(
    file_list: UploadFile | list[UploadFile] = File(...),  # type: ignore
    project: Project = Depends(dependency=get_authenticated_project),
) -> WorkerTaskResult:
    """
    Endpoint to queue a file for processing.

    Args:
            file_list (UploadFile | list[UploadFile]): The file or list of files to queue.
    """
    # Get project ID.
    project_id = project.id

    # Push file to Redis queue.
    result = await push_upload_file_to_redis_queue(file_list=file_list, project_id=project_id)

    return WorkerTaskResult(task_id=result.id, message="File(s) has been queued for processing.")  # type: ignore


@router.delete(path="/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_endpoint(
    file_id: str,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> None:
    """
    Endpoint to delete a file by its ID.

    Args:
            file_id (str): The ID of the file to delete.
    """
    # Get project ID.
    project_id = project.id

    # Delete file record.
    await delete_file_records(file_id=file_id, project_id=project_id, db=db)
