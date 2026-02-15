"""
Module with all models related to all task details.
"""

from pydantic import BaseModel, Field

from backend.database.enums import FileFormat
from backend.database.models import CommonModel, CommonRequestModel, CommonResponseModel


# Schemas.
class _TaskDetail(CommonModel):
    """
    Main task configuration model.
    """

    # Fields.
    file_format: list[FileFormat] = Field(..., description="The file formats supported for the task.")


class _TaskDetailDB(CommonResponseModel, _TaskDetail):
    """
    Task configuration model for database representation.
    """

    pass


class _TaskDetailCreate(_TaskDetail, CommonRequestModel):
    """
    Task configuration model for creating a new task configuration.
    """

    pass


# - Schemas for different task types.
class _ClassTaskDetail(BaseModel):
    """
    Task configuration for class-related tasks.
    """

    class_name_list: list[str] = Field(default_factory=list, description="List of class names supported for the task.")


# - Image Task Configs.
class _ImageTaskDetail(_TaskDetail):
    """
    Task configuration for image-related tasks.
    """

    file_format: list[FileFormat] = Field(
        default_factory=FileFormat.get_image_formats,
        description="The image file formats supported for the task.",
        frozen=True,
    )


class _VisualTaskDetail(_ImageTaskDetail):
    """
    Task configuration for visual-related tasks.
    """

    pass


# * Image Classification Task Configs.
class _ImageClassificationTaskDetail(_ImageTaskDetail, _ClassTaskDetail):
    """
    Task configuration for image classification tasks.
    """

    pass


class ImageClassificationTaskDetail(_ImageClassificationTaskDetail, _TaskDetailDB):
    """
    Task configuration for image classification tasks, including database representation.
    """

    pass


class ImageClassificationTaskDetailCreate(_TaskDetailCreate, _ImageClassificationTaskDetail):
    """
    Task configuration for creating image classification tasks.
    """

    pass


# * Object Detection Task Configs.
class _ObjectDetectionTaskDetail(_ClassTaskDetail, _VisualTaskDetail):
    """
    Task configuration for object detection tasks.
    """

    pass


class ObjectDetectionTaskDetail(_ObjectDetectionTaskDetail, _TaskDetailDB):
    """
    Task configuration for object detection tasks, including database representation.
    """

    pass


class ObjectDetectionTaskDetailCreate(_TaskDetailCreate, _ObjectDetectionTaskDetail):
    """
    Task configuration for creating object detection tasks.
    """

    pass


# * Image Caption Task Configs.
class _ImageCaptionTaskDetail(_ImageTaskDetail):
    """
    Task configuration for image caption tasks.
    """

    pass


class ImageCaptionTaskDetail(_ImageCaptionTaskDetail, _TaskDetailDB):
    """
    Task configuration for image caption tasks, including database representation.
    """

    pass


class ImageCaptionTaskDetailCreate(_TaskDetailCreate, _ImageCaptionTaskDetail):
    """
    Task configuration for creating image caption tasks.
    """

    pass


# * Object Caption Task Configs.
class _ObjectCaptionTaskDetail(_ImageTaskDetail):
    """
    Task configuration for object caption tasks.
    """

    pass


class ObjectCaptionTaskDetail(_ObjectCaptionTaskDetail, _TaskDetailDB):
    """
    Task configuration for object caption tasks, including database representation.
    """

    pass


class ObjectCaptionTaskDetailCreate(_TaskDetailCreate, _ObjectCaptionTaskDetail):
    """
    Task configuration for creating object caption tasks.
    """

    pass


# - Text Task Configs.
class _TextTaskDetail(_TaskDetail):
    """
    Task configuration for text-related tasks.
    """

    file_format: list[FileFormat] = Field(
        default_factory=FileFormat.get_text_formats,
        description="The text file formats supported for the task.",
        frozen=True,
    )


# * Text Classification Task Configs.
class _TextClassificationTaskDetail(_TextTaskDetail, _ClassTaskDetail):
    """
    Task configuration for text classification tasks.
    """

    pass


class TextClassificationTaskDetail(_TextClassificationTaskDetail, _TaskDetailDB):
    """
    Task configuration for text classification tasks, including database representation.
    """

    pass


class TextClassificationTaskDetailCreate(_TaskDetailCreate, _TextClassificationTaskDetail):
    """
    Task configuration for creating text classification tasks.
    """

    pass


# - Text Tagging Task Configs.
class _TextTaggingTaskDetail(_TextTaskDetail):
    """
    Task configuration for text tagging tasks.
    """

    pass


class TextTaggingTaskDetail(_TextTaggingTaskDetail, _TaskDetailDB):
    """
    Task configuration for text tagging tasks, including database representation.
    """

    pass


class TextTaggingTaskDetailCreate(_TaskDetailCreate, _TextTaggingTaskDetail):
    """
    Task configuration for creating text tagging tasks.
    """

    pass
