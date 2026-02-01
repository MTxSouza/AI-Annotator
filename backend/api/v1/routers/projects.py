"""
Module with all endpoints related to project operations.
"""
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.params import Param
from fastapi.requests import Request
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.projects import (Create, Project, ProjectSimple,
                                            Update)
from backend.api.v1.utils.projects import (create_project, delete_project,
                                           get_authenticated_project,
                                           get_project_by_id, get_projects,
                                           is_project_name_exists,
                                           update_project)
from backend.database.configs import DatabaseConfig
from backend.limiter import limiter

# Instantiate the router.
router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[Depends(dependency=DatabaseConfig.get_database)]
)

# Endpoints.
@router.get(path="/", name="Get Projects", response_model=list[ProjectSimple], status_code=status.HTTP_200_OK)
async def get_projects_endpoint(
    limit: int = Param(default=10, ge=1, le=100),
    offset: int = Param(default=0, ge=0),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> list[ProjectSimple]:
    """
    Endpoint to get all projects.

    Returns:
        list[ProjectSimple]: List of all projects.
    """
    return await get_projects(db=db, limit=limit, offset=offset)

@router.get(path="/{id}", name="Get Project", response_model=Project, status_code=status.HTTP_200_OK)
async def get_project_endpoint(project: Project = Depends(dependency=get_authenticated_project)) -> Project:
    """
    Endpoint to get a project by its ID.

    Args:
        id (str): The ID of the project.

    Returns:
        ProjectDetail: The project with the given ID.
    """
    return project

@router.post(path="/", name="Create Project", response_model=Project, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_project_endpoint(
    request: Request,
    project: Create,
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> Project:
    """
    Endpoint to create a new project.

    Args:
        project (ProjectCreate): The project data to create.

    Returns:
        Project: The created project.
    """
    # Check if a project with the same name already exists.
    if await is_project_name_exists(db=db, project_name=project.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project with the same name already exists")

    # Create the project.
    new_project = await create_project(db=db, project_data=project.model_dump())

    return new_project

@router.put(path="/{id}", name="Update Project", response_model=Project, status_code=status.HTTP_201_CREATED)
async def update_project_endpoint(
    update: Update,
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> Project:
    """
    Endpoint to update an existing project.

    Args:
        id (str): The ID of the project to update.
        project (ProjectUpdate): The updated project data.

    Returns:
        Project: The updated project.
    """
    # Get project ID.
    id = str(project.id)

    # Update the project.
    updated_project = await update_project(db=db, project_id=id, project_data=update.model_dump(exclude_unset=True))

    return updated_project

@router.delete(path="/{id}", name="Delete Project", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    project: Project = Depends(dependency=get_authenticated_project),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> None:
    """
    Endpoint to delete a project by its ID.

    Args:
        id (str): The ID of the project to delete.
    """
    # Get project ID.
    id = str(project.id)

    # Check if the project exists.
    if await get_project_by_id(db=db, project_id=id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Delete the project.
    await delete_project(db=db, project_id=id)
