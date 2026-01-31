"""
Module with all utilities related to project operations.
"""
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.utils.auth import (decode_access_token, hash_password,
                                       oauth2_scheme, throw_bearer_error)
from backend.database.configs import Collections, DatabaseConfig
from backend.database.types import PyObjectId


# Functions.
def setup_private_field(project: dict) -> dict:
    """
    Utility function to check and setup the private
    field project with it has a password.

    Args:
        project (dict): The project data.

    Returns:
        dict: The project with the private field set.
    """
    # Set private field.
    project["is_private"] = project.get("hashed_password") is not None
    return project

async def get_projects(
    db: AsyncDatabase,
    limit: int,
    offset: int
    ) -> list[dict]:
    """
    Utility function to get all projects from the database.

    Args:
        db (AsyncDatabase): The database instance.
        limit (int): The maximum number of projects to retrieve.
        offset (int): The number of projects to skip.

    Returns:
        list[dict]: List of all projects.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Query projects.
    cursor = collection.find().skip(offset).limit(limit)
    projects = await cursor.to_list()

    # Setup private field for each project.
    projects = list(map(setup_private_field, projects))

    return projects

async def get_project_by_id(
    db: AsyncDatabase,
    project_id: str
    ) -> dict | None:
    """
    Utility function to get a project by its ID.

    Args:
        db (AsyncDatabase): The database instance.
        project_id (str): The ID of the project.

    Returns:
        dict | None: The project with the given ID or None if not found.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Query project by ID.
    project_id = PyObjectId(oid=project_id)
    project = await collection.find_one({"_id": project_id})

    # Setup private field if project exists.
    if project is not None:
        project = setup_private_field(project=project)

    return project

async def get_authenticated_project(
    id: str = Path(..., description="The ID of the project."),
    token: str = Depends(dependency=oauth2_scheme),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ):
    """
    Utility function to get an authenticated project by its ID.

    Args:
        id (str): The ID of the project.
        token (str): The access token.
        db (AsyncDatabase): The database instance.

    Returns:
        dict | None: The authenticated project or None if not found.
    """
    # Get project.
    project = await get_project_by_id(db=db, project_id=id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if the project is private.
    if not project.get("is_private"):
        return project

    # Check if the token is valid.
    if token is None:
        throw_bearer_error(
            message="Not authenticated to access this private project",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Validate token subject.
    decoded_token = decode_access_token(token=token)
    if not decoded_token:
        throw_bearer_error(
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if decoded_token.get("sub") != str(project["_id"]):
        throw_bearer_error(
            message="Token subject does not match project ID",
            status_code=status.HTTP_403_FORBIDDEN
        )

    return project

async def get_project_by_name(
    db: AsyncDatabase,
    project_name: str
    ) -> dict | None:
    """
    Utility function to get a project by its name.

    Args:
        db (AsyncDatabase): The database instance.
        project_name (str): The name of the project.

    Returns:
        dict | None: The project with the given name or None if not found.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Query project by name.
    project = await collection.find_one({"name": project_name})

    # Setup private field if project exists.
    if project is not None:
        project = setup_private_field(project=project)

    return project

def set_project_password(
    project_data: dict
    ) -> dict:
    """
    Utility function to check and hash the password
    in the project update data if it exists.

    Args:
        project_data (dict): The project update data.

    Returns:
        dict: The project update data with hashed password if applicable.
    """
    # Check if the project contains a password.
    if project_data.get("password"):
        project_data["hashed_password"] = hash_password(password=project_data.pop("password"))
    else:
        project_data["hashed_password"] = None
    return project_data

async def create_project(
    db: AsyncDatabase,
    project_data: dict
    ) -> dict:
    """
    Utility function to create a new project.

    Args:
        db (AsyncDatabase): The database instance.
        project_data (dict): The project data to create.

    Returns:
        dict: The created project.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Check if the project contains a password.
    project_data = set_project_password(project_data=project_data)

    # Insert new project.
    result = await collection.insert_one(project_data)

    # Retrieve the created project.
    created_project = await get_project_by_id(db=db, project_id=result.inserted_id)

    return created_project

async def update_project(
    db: AsyncDatabase,
    project_id: str,
    project_data: dict
    ) -> dict:
    """
    Utility function to update an existing project.

    Args:
        db (AsyncDatabase): The database instance.
        project_id (str): The ID of the project to update.
        project_data (dict): The updated project data.

    Returns:
        dict: The updated project.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Check if the project contains a password.
    project_data = set_project_password(project_data=project_data)

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
    db: AsyncDatabase,
    project_id: str
    ) -> None:
    """
    Utility function to delete a project by its ID.

    Args:
        db (AsyncDatabase): The database instance.
        project_id (str): The ID of the project to delete.
    """
    # Get projects collection.
    collection = db.get_collection(name=Collections.PROJECTS.value.name)

    # Delete the project.
    project_id = PyObjectId(oid=project_id)
    await collection.delete_one({"_id": project_id})
