"""
Main module with all schemas used in Projects collection.
"""
from typing import Optional

from pydantic import Field

from backend.database.models import (CommonRequestModel, CommonResponseModel,
                                     CommonUpdateModel)
from backend.database.types import TaskType


# Schemas.
class Project(CommonResponseModel):
    """
    Project model.
    """
    name: str = Field(..., description="The name of the project.")
    description: Optional[str] = Field(default=None, description="The description of the project.")
    task_type: TaskType = Field(..., description="The type of task for the project.")

class ProjectDetail(Project):
    """
    Project model with detailed information.
    """
    num_samples: Optional[int] = Field(default=0, description="The number of samples in the project.")
    num_annotations: Optional[int] = Field(default=0, description="The number of annotations in the project.")

class ProjectCreate(CommonRequestModel):
    """
    Project creation model.
    """
    name: str = Field(..., description="The name of the project.")
    task_type: TaskType = Field(..., description="The type of task for the project.")

class ProjectUpdate(CommonUpdateModel):
    """
    Project update model.
    """
    name: Optional[str] = Field(default=None, description="The name of the project.")
    description: Optional[str] = Field(default=None, description="The description of the project.")