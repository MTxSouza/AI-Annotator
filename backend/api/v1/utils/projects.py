"""
Module with all utilities related to project operations.
"""
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.projects import Project
from backend.api.v1.utils.auth import (decode_access_token, oauth2_scheme,
                                       throw_bearer_error)
from backend.api.v1.utils.task_configs import setup_task_config
from backend.database.configs import Collections, DatabaseConfig
from backend.database.types import PyObjectId


# Functions.
async def get_projects(
    limit: int,
    offset: int,
    db: AsyncDatabase
    ) -> list[dict]:
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

async def get_project_by_id(
    project_id: str,
    db: AsyncDatabase
    ) -> dict | None:
    """
    Utility function to get a project by its ID.

    Args:
        project_id (str): The ID of the project.
        db (AsyncDatabase): The database instance.

    Returns:
        dict | None: The project with the given ID or None if not found.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Query project by ID.
    project_id = PyObjectId(oid=project_id)
    pipeline = [
        {"$match": {"_id": project_id}},
        {"$lookup": {
            "from": Collections.TASK_CONFIGS.value.name,
            "localField": "_id",
            "foreignField": "project_id",
            "as": "configs"
        }},
        {"$set": {"configs": {"$first": "$configs"}}}
    ]
    cursor = await collection.aggregate(pipeline)
    project = await cursor.to_list(length=1)
    project = project.pop() if project else None

    return project

async def is_project_name_exists(
    project_name: str,
    db: AsyncDatabase
    ) -> bool:
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
    existing_project = await collection.find_one({"name": project_name})
    return existing_project is not None

async def get_authenticated_project(
    id: str = Path(..., description="The ID of the project."),
    token: str = Depends(dependency=oauth2_scheme),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> Project:
    """
    Utility function to get an authenticated project by its ID.

    Args:
        id (str): The ID of the project.
        token (str): The access token.
        db (AsyncDatabase): The database instance.

    Returns:
        Project: The authenticated project.
    """
    # Get project.
    project = await get_project_by_id(db=db, project_id=id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if the project is private.
    if not project.get("hashed_password"):
        return Project.model_validate(obj=project)

    # Check if the token is valid.
    if token is None:
        throw_bearer_error(
            message="Not authenticated to access this private project",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Get decoded token.
    decoded_token = decode_access_token(token=token)

    # Check token subject matches project ID.
    if decoded_token.get("sub") != str(project["_id"]):
        throw_bearer_error(
            message="Token subject does not match project ID",
            status_code=status.HTTP_403_FORBIDDEN
        )

    return Project.model_validate(obj=project)

async def create_project(
    project_data: dict,
    db: AsyncDatabase
    ) -> dict:
    """
    Utility function to create a new project.

    Args:
        project_data (dict): The project data to create.
        db (AsyncDatabase): The database instance.

    Returns:
        dict: The created project.
    """
    # Get project and task config collections.
    project_collection = db.get_collection(name=Collections.PROJECTS.value.name)
    task_config_collection = db.get_collection(name=Collections.TASK_CONFIGS.value.name)

    # Insert new project.
    result = await project_collection.insert_one(project_data)
    task_config_data = setup_task_config(project_id=result.inserted_id, task=project_data["task"])
    await task_config_collection.insert_one(task_config_data)

    # Retrieve the created project.
    created_project = await get_project_by_id(db=db, project_id=result.inserted_id)

    return created_project

async def update_project(
    project_id: str,
    project_data: dict,
    db: AsyncDatabase
    ) -> dict:
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
    project_id = PyObjectId(oid=project_id)
    await collection.update_one(
        {"_id": project_id},
        {"$set": project_data}
    )

    # Retrieve the updated project.
    updated_project = await get_project_by_id(db=db, project_id=project_id)

    return updated_project

async def delete_project(
    project_id: str,
    db: AsyncDatabase
    ) -> None:
    """
    Utility function to delete a project by its ID.

    Args:
        project_id (str): The ID of the project to delete.
        db (AsyncDatabase): The database instance.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Delete the project.
    project_id = PyObjectId(oid=project_id)
    await collection.delete_one({"_id": project_id})
