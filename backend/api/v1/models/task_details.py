"""
Module with all models related to all task details.
"""

from pydantic import Field

from backend.database.enums import FileFormat
from backend.database.models import CommonModel


# Schemas.
class _TaskDetail(CommonModel):
    """
    Main task configuration model.
    """

    # Fields.
    file_format: list[FileFormat] = Field(..., description="The file formats supported for the task.")


# - Schemas for different task types.
class _ClassTaskDetail(_TaskDetail):
    """
    Task configuration for class-related tasks.
    """

    class_name_list: list[str] = Field(default_factory=list, description="List of class names supported for the task.")
    class_name_histogram: dict[str, int] = Field(
        default_factory=dict, description="Histogram of class names in the samples for the task."
    )


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
class ImageClassificationTaskDetail(_ImageTaskDetail, _ClassTaskDetail):
    """
    Task configuration for image classification tasks.
    """

    pass


# * Object Detection Task Configs.
class ObjectDetectionTaskDetail(_VisualTaskDetail, _ClassTaskDetail):
    """
    Task configuration for object detection tasks.
    """

    pass


# * Image Caption Task Configs.
class ImageCaptionTaskDetail(_ImageTaskDetail):
    """
    Task configuration for image caption tasks.
    """

    pass


# * Object Caption Task Configs.
class ObjectCaptionTaskDetail(_ImageTaskDetail):
    """
    Task configuration for object caption tasks.
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
class TextClassificationTaskDetail(_TextTaskDetail, _ClassTaskDetail):
    """
    Task configuration for text classification tasks.
    """

    pass


# - Text Tagging Task Configs.
class TextTaggingTaskDetail(_TextTaskDetail, _ClassTaskDetail):
    """
    Task configuration for text tagging tasks.
    """

    pass
