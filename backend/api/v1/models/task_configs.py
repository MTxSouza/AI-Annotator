"""
Module with all models related to all task configurations.
"""

from pydantic import BaseModel, Field

from backend.database.enums import FileFormat, PyObjectId
from backend.database.models import CommonModel, CommonRequestModel, CommonResponseModel, CommonUpdateModel


# Schemas.
class _TaskConfig(CommonModel):
    """
    Main task configuration model.
    """

    # Fields.
    project_id: PyObjectId = Field(..., description="The ID of the project associated with this task configuration.")
    file_format: list[FileFormat] = Field(..., description="The file formats supported for the task.")


class _TaskConfigDB(CommonResponseModel, _TaskConfig):
    """
    Task configuration model for database representation.
    """

    pass


class _TaskConfigCreate(_TaskConfig, CommonRequestModel):
    """
    Task configuration model for creating a new task configuration.
    """

    pass


class _TaskConfigUpdate(CommonUpdateModel):
    """
    Task configuration model for updating an existing task configuration.
    """

    pass


# - Schemas for different task types.
class _ClassTaskConfig(BaseModel):
    """
    Task configuration for class-related tasks.
    """

    class_name_list: list[str] = Field(default_factory=list, description="List of class names supported for the task.")


class _ClassTaskConfigUpdate(_TaskConfigUpdate):
    """
    Task configuration for updating class-related tasks.
    """

    pass


# - Image Task Configs.
class _ImageTaskConfig(_TaskConfig):
    """
    Task configuration for image-related tasks.
    """

    file_format: list[FileFormat] = Field(
        default_factory=FileFormat.get_image_formats,
        description="The image file formats supported for the task.",
        frozen=True,
    )


class _VisualTaskConfig(_ImageTaskConfig):
    """
    Task configuration for visual-related tasks.
    """

    pass


class _VisualTaskConfigUpdate(_TaskConfigUpdate):
    """
    Task configuration for updating visual-related tasks.
    """

    pass


# * Image Classification Task Configs.
class _ImageClassificationTaskConfig(_ImageTaskConfig, _ClassTaskConfig):
    """
    Task configuration for image classification tasks.
    """

    pass


class ImageClassificationTaskConfig(_ImageClassificationTaskConfig, _TaskConfigDB):
    """
    Task configuration for image classification tasks, including database representation.
    """

    pass


class ImageClassificationTaskConfigCreate(_TaskConfigCreate, _ImageClassificationTaskConfig):
    """
    Task configuration for creating image classification tasks.
    """

    pass


class ImageClassificationTaskConfigUpdate(_ClassTaskConfigUpdate):
    """
    Task configuration for updating image classification tasks.
    """

    pass


# * Object Detection Task Configs.
class _ObjectDetectionTaskConfig(_ClassTaskConfig, _VisualTaskConfig):
    """
    Task configuration for object detection tasks.
    """

    pass


class ObjectDetectionTaskConfig(_ObjectDetectionTaskConfig, _TaskConfigDB):
    """
    Task configuration for object detection tasks, including database representation.
    """

    pass


class ObjectDetectionTaskConfigCreate(_TaskConfigCreate, _ObjectDetectionTaskConfig):
    """
    Task configuration for creating object detection tasks.
    """

    pass


class ObjectDetectionTaskConfigUpdate(_ClassTaskConfigUpdate, _VisualTaskConfigUpdate):
    """
    Task configuration for updating object detection tasks.
    """

    pass


# * Image Caption Task Configs.
class _ImageCaptionTaskConfig(_ImageTaskConfig):
    """
    Task configuration for image caption tasks.
    """

    pass


class ImageCaptionTaskConfig(_ImageCaptionTaskConfig, _TaskConfigDB):
    """
    Task configuration for image caption tasks, including database representation.
    """

    pass


class ImageCaptionTaskConfigCreate(_TaskConfigCreate, _ImageCaptionTaskConfig):
    """
    Task configuration for creating image caption tasks.
    """

    pass


class ImageCaptionTaskConfigUpdate(_TaskConfigUpdate):
    """
    Task configuration for updating image caption tasks.
    """

    pass


# * Object Caption Task Configs.
class _ObjectCaptionTaskConfig(_ImageTaskConfig):
    """
    Task configuration for object caption tasks.
    """

    pass


class ObjectCaptionTaskConfig(_ObjectCaptionTaskConfig, _TaskConfigDB):
    """
    Task configuration for object caption tasks, including database representation.
    """

    pass


class ObjectCaptionTaskConfigCreate(_TaskConfigCreate, _ObjectCaptionTaskConfig):
    """
    Task configuration for creating object caption tasks.
    """

    pass


class ObjectCaptionTaskConfigUpdate(_VisualTaskConfigUpdate):
    """
    Task configuration for updating object caption tasks.
    """

    pass


# - Text Task Configs.
class _TextTaskConfig(_TaskConfig):
    """
    Task configuration for text-related tasks.
    """

    file_format: list[FileFormat] = Field(
        default_factory=FileFormat.get_text_formats,
        description="The text file formats supported for the task.",
        frozen=True,
    )


# * Text Classification Task Configs.
class _TextClassificationTaskConfig(_TextTaskConfig, _ClassTaskConfig):
    """
    Task configuration for text classification tasks.
    """

    pass


class TextClassificationTaskConfig(_TextClassificationTaskConfig, _TaskConfigDB):
    """
    Task configuration for text classification tasks, including database representation.
    """

    pass


class TextClassificationTaskConfigCreate(_TaskConfigCreate, _TextClassificationTaskConfig):
    """
    Task configuration for creating text classification tasks.
    """

    pass


class TextClassificationTaskConfigUpdate(_ClassTaskConfigUpdate):
    """
    Task configuration for updating text classification tasks.
    """

    pass


# - Text Tagging Task Configs.
class _TextTaggingTaskConfig(_TextTaskConfig):
    """
    Task configuration for text tagging tasks.
    """

    pass


class TextTaggingTaskConfig(_TextTaggingTaskConfig, _TaskConfigDB):
    """
    Task configuration for text tagging tasks, including database representation.
    """

    pass


class TextTaggingTaskConfigCreate(_TaskConfigCreate, _TextTaggingTaskConfig):
    """
    Task configuration for creating text tagging tasks.
    """

    pass


class TextTaggingTaskConfigUpdate(_TaskConfigUpdate):
    """
    Task configuration for updating text tagging tasks.
    """

    pass
