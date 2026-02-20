"""
Main module with all schemas used in Projects collection.
"""

from pydantic import Field, computed_field

from backend.api.v1.models.task_details import (
    AudioTranscriptionTaskDetail,
    ImageCaptionTaskDetail,
    ImageClassificationTaskDetail,
    ObjectCaptionTaskDetail,
    ObjectDetectionTaskDetail,
    TextClassificationTaskDetail,
    TextTaggingTaskDetail,
)
from backend.api.v1.utils.auth import hash_password
from backend.database.enums import Task
from backend.database.models import CommonRequestModel, CommonResponseModel, CommonUpdateModel

# Global Variables.
__MIN_NAME_LENGTH__: int = 1
__MAX_NAME_LENGTH__: int = 64
__MAX_DESCRIPTION_LENGTH__: int = 500
__PROJECT_DETAILS__ = (
    ObjectDetectionTaskDetail
    | ImageCaptionTaskDetail
    | ObjectCaptionTaskDetail
    | ImageClassificationTaskDetail
    | TextClassificationTaskDetail
    | TextTaggingTaskDetail
    | AudioTranscriptionTaskDetail
)


# Schemas.
class ProjectSimple(CommonResponseModel):
    """
    Simple Project model.
    """

    # Fields.
    name: str = Field(
        ..., min_length=__MIN_NAME_LENGTH__, max_length=__MAX_NAME_LENGTH__, description="The name of the project."
    )
    description: str | None = Field(
        default=None, max_length=__MAX_DESCRIPTION_LENGTH__, description="The description of the project."
    )
    task: Task = Field(..., description="The task for the project.")
    hashed_password: str | None = Field(
        default=None, exclude=True, description="The hashed password for the project if it is private."
    )

    # Computed Fields.
    @computed_field(description="Whether the project is private or public.")
    def is_private(self) -> bool:
        """
        Computed field to determine if the project is private.

        Returns:
                bool: True if the project is private, False otherwise.
        """
        return self.hashed_password is not None


class Create(CommonRequestModel):
    """
    Project creation model.
    """

    # Fields.
    name: str = Field(
        ..., min_length=__MIN_NAME_LENGTH__, max_length=__MAX_NAME_LENGTH__, description="The name of the project."
    )
    description: str | None = Field(
        default=None, max_length=__MAX_DESCRIPTION_LENGTH__, description="The description of the project."
    )
    task: Task = Field(..., description="The task for the project.")
    password: str | None = Field(
        default=None, min_length=1, exclude=True, description="The password for the project if it should be private."
    )

    # Computed Fields.
    @computed_field(description="The hashed password for the project if it is private.")
    def hashed_password(self) -> str | None:
        if self.password:
            return hash_password(password=self.password)
        return None


class Update(CommonUpdateModel):
    """
    Project update model.
    """

    # Fields.
    name: str | None = Field(default=None, min_length=__MIN_NAME_LENGTH__, max_length=__MAX_NAME_LENGTH__)  # type: ignore
    description: str | None = Field(
        default=None, max_length=__MAX_DESCRIPTION_LENGTH__, description="The description of the project."
    )
    password: str | None = Field(
        default=None, min_length=1, exclude=True, description="The password for the project if it should be private."
    )

    # Computed Fields.
    @computed_field(description="The hashed password for the project if it is private.")
    def hashed_password(self) -> str | None:
        if self.password:
            return hash_password(password=self.password)
        elif "password" in self.model_fields_set:
            return None
        return None


class Project(ProjectSimple):
    """
    Project model.
    """

    # Additional Fields.
    details: __PROJECT_DETAILS__ = Field(..., description="The task details for the project.")
