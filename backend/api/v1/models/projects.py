"""
Main module with all schemas used in Projects collection.
"""
from typing import Optional

from pydantic import BaseModel, Field

from backend.database.models import (CommonRequestModel, CommonResponseModel,
                                     CommonUpdateModel)
from backend.database.types import TaskType


# Schemas.
class _DB(BaseModel):
    """
    Project model in the database.
    """
    # Fields.
    name: str = Field(..., description="The name of the project.")
    description: Optional[str] = Field(default=None, description="The description of the project.")
    task_type: TaskType = Field(..., description="The type of task for the project.")
    password_hash: Optional[str] = Field(default=None, description="The hashed password for the project if it is private.")

class Create(_DB, CommonRequestModel):
    """
    Project creation model.
    """
    # Fields.
    password: Optional[str] = Field(default=None, min_length=1, description="The password for the project if it should be private.")

    # To be excluded.
    password_hash: Optional[str] = Field(default=None, exclude=True)

class Update(_DB, CommonUpdateModel):
    """
    Project update model.
    """
    # Fields.
    name: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=1, description="The password for the project if it should be private.")

    # To be excluded.
    task_type: Optional[TaskType] = Field(default=None, exclude=True)
    password_hash: Optional[str] = Field(default=None, exclude=True)

class ProjectSimple(_DB, CommonResponseModel):
    """
    Simple Project model.
    """
    # Fields.
    is_private: bool = Field(default=False, description="Whether the project is private or public.")

    # To be excluded.
    password_hash: Optional[str] = Field(default=None, exclude=True)

class Project(ProjectSimple):
    """
    Project model.
    """
    # Additional Fields.
    num_samples: Optional[int] = Field(default=0, description="The number of samples in the project.")
    num_annotations: Optional[int] = Field(default=0, description="The number of annotations in the project.")
