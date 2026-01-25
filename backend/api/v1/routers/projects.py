"""
Module with all endpoints related to project operations.
"""
from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.projects import (Project, ProjectCreate,
                                            ProjectDetail, ProjectUpdate)
from backend.database.configs import DatabaseConfig

# Instantiate the router.
router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# Endpoints.
@router.get(path="/", response_model=list[Project], status_code=status.HTTP_200_OK)
async def get_projects(db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)) -> list[Project]:
    """
    Endpoint to get all projects.

    Returns:
        list[Project]: List of all projects.
    """
    pass  # TODO: Implementation goes here.

@router.get(path="/{id}", response_model=ProjectDetail, status_code=status.HTTP_200_OK)
async def get_project(id: str, db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)) -> ProjectDetail:
    """
    Endpoint to get a project by its ID.

    Args:
        id (str): The ID of the project.

    Returns:
        ProjectDetail: The project with the given ID.
    """
    pass  # TODO: Implementation goes here.

@router.post(path="/", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)) -> ProjectDetail:
    """
    Endpoint to create a new project.

    Args:
        project (ProjectCreate): The project data to create.

    Returns:
        ProjectDetail: The created project.
    """
    pass  # TODO: Implementation goes here.

@router.put(path="/{id}", response_model=ProjectDetail, status_code=status.HTTP_200_OK)
async def update_project(id: str, project: ProjectUpdate, db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)) -> ProjectDetail:
    """
    Endpoint to update an existing project.

    Args:
        id (str): The ID of the project to update.
        project (ProjectUpdate): The updated project data.

    Returns:
        ProjectDetail: The updated project.
    """
    pass  # TODO: Implementation goes here.

@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: str, db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)) -> None:
    """
    Endpoint to delete a project by its ID.

    Args:
        id (str): The ID of the project to delete.
    """
    pass  # TODO: Implementation goes here.
