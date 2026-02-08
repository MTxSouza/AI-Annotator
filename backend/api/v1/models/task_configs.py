"""
Module with all models related to all task configurations.
"""

from pydantic import Field

from backend.database.enums import FileFormat, PyObjectId
from backend.database.models import CommonResponseModel


# Schemas.
class __TaskConfig(CommonResponseModel):
    """
    Main task configuration model.
    """

    # Fields.
    project_id: PyObjectId | str = Field(
        ..., description="The ID of the project associated with this task configuration."
    )
    file_format: list[FileFormat] = Field(..., description="The file formats supported for the task.")


# - Images.
class __ImageTaskConfig(__TaskConfig):
    """
    Image task configuration model.
    """

    # Fields.
    file_format: list[FileFormat] = Field(
        default=FileFormat.get_image_formats(), description="The image file formats supported for the task."
    )


class __ObjectTaskConfig(__ImageTaskConfig):
    """
    Object task configuration model.
    """

    # Fields.
    class_names: list[str] = Field(default=[], description="The names of the object classes for the task.")


class ObjectDetectionTaskConfig(__ObjectTaskConfig):
    """
    Object detection task configuration model.
    """

    pass


class SemanticSegmentationTaskConfig(__ObjectTaskConfig):
    """
    Semantic segmentation task configuration model.
    """

    pass


# - Texts.
class __TextTaskConfig(__TaskConfig):
    """
    Text task configuration model.
    """

    # Fields.
    file_format: list[FileFormat] = Field(
        default=FileFormat.get_text_formats(), description="The text file formats supported for the task."
    )


# - Audios.
class __AudioTaskConfig(__TaskConfig):
    """
    Audio task configuration model.
    """

    # Fields.
    file_format: list[FileFormat] = Field(
        default=FileFormat.get_audio_formats(), description="The audio file formats supported for the task."
    )
