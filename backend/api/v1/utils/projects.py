"""
Module with all utilities related to project operations.
"""

from typing import Annotated

from fastapi import Cookie, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.projects import Project
from backend.api.v1.utils.auth import decode_access_token, throw_bearer_error
from backend.api.v1.utils.files import unset_project_id_in_file_records
from backend.api.v1.utils.samples import delete_samples_by_project_id
from backend.api.v1.utils.task_details import setup_task_detail
from backend.database.configs import Collections, DatabaseConfig
from backend.database.enums import PyObjectId


# Functions.
async def get_projects(limit: int, offset: int, db: AsyncDatabase) -> list[dict]:
    """
    Utility function to get all projects from the database.

    Args:
            limit (int): The maximum number of projects to retrieve.
            offset (int): The number of projects to skip.
            db (AsyncDatabase): The database instance.

    Returns:
            list[dict]: List of all projects.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Query projects.
    cursor = collection.find().skip(offset).limit(limit)
    projects = await cursor.to_list()

    return projects


async def get_project_by_id(project_id: str | PyObjectId, db: AsyncDatabase) -> dict | None:
    """
    Utility function to get a project by its ID.

    Args:
            project_id (str | PyObjectId): The ID of the project.
            db (AsyncDatabase): The database instance.

    Returns:
            dict | None: The project with the given ID or None if not found.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Query project by ID.
    project_id_obj = PyObjectId(oid=project_id)
    project = await collection.find_one(filter={"_id": project_id_obj})

    # Setup task detail document.
    if project:
        task_detail_data = await setup_task_detail(task=project["task"], project_id=project_id, db=db)
        project["details"] = task_detail_data

    return project


async def is_project_name_exists(project_name: str, db: AsyncDatabase) -> bool:
    """
    Utility function to check if a project name already exists.

    Args:
            project_name (str): The name of the project.
            db (AsyncDatabase): The database instance.

    Returns:
            bool: True if the project name exists, False otherwise.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Check if a project with the same name exists.
    existing_project = await collection.find_one({"name": project_name}, {"_id": 1})
    return existing_project is not None


async def get_authenticated_project(
    project_id: str = Path(..., description="The ID of the project."),  # type: ignore
    access_token: Annotated[str | None, Cookie()] = None,
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
) -> Project:
    """
    Utility function to get an authenticated project by its ID.

    Args:
            project_id (str): The ID of the project.
            access_token (str | None): The access token from the cookie. (Default: None)
            db (AsyncDatabase): The database instance.

    Returns:
            Project: The authenticated project.
    """
    # Get project.
    project = await get_project_by_id(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if the project needs authentication.
    if not project.get("hashed_password"):
        return Project.model_validate(obj=project)

    # Check if access token is provided.
    if access_token is None:
        throw_bearer_error(
            message="Not authenticated to access this private project", status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Get decoded token.
    decoded_token = decode_access_token(token=access_token)  # type: ignore
    if decoded_token is None:
        throw_bearer_error(message="Invalid access token", status_code=status.HTTP_401_UNAUTHORIZED)

    # Check token subject matches project ID.
    if decoded_token.get("sub") != str(project["_id"]):  # type: ignore
        throw_bearer_error(message="Token subject does not match project ID", status_code=status.HTTP_403_FORBIDDEN)

    return Project.model_validate(obj=project)


async def create_project(project_data: dict, db: AsyncDatabase) -> dict:
    """
    Utility function to create a new project.

    Args:
            project_data (dict): The project data to create.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The created project.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Insert new project.
    result = await collection.insert_one(project_data)

    # Retrieve the created project.
    created_project = await get_project_by_id(db=db, project_id=result.inserted_id)

    return created_project  # type: ignore


async def update_project(project_id: str, project_data: dict, db: AsyncDatabase) -> dict:
    """
    Utility function to update an existing project.

    Args:
            project_id (str): The ID of the project to update.
            project_data (dict): The updated project data.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The updated project.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Update the project.
    project_id_obj = PyObjectId(oid=project_id)
    await collection.update_one({"_id": project_id_obj}, {"$set": project_data})

    # Retrieve the updated project.
    updated_project = await get_project_by_id(db=db, project_id=project_id_obj)

    return updated_project  # type: ignore


async def delete_project(project_id: str, db: AsyncDatabase) -> None:
    """
    Utility function to delete a project by its ID.

    Args:
            project_id (str): The ID of the project to delete.
            db (AsyncDatabase): The database instance.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Delete samples associated with the project.
    await delete_samples_by_project_id(project_id=project_id, db=db)

    # Delete project ID from associated files.
    await unset_project_id_in_file_records(project_id=project_id, db=db)

    # Delete the project.
    project_id_obj = PyObjectId(oid=project_id)
    await collection.delete_one({"_id": project_id_obj})
