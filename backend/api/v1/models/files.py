"""
Main module with all schemas used in Files collection.
"""

from pydantic import BaseModel, Field, computed_field, field_validator

from backend.database.enums import FileFormat, FileUploadStatus, PyObjectId
from backend.database.models import CommonModel, CommonRequestModel, CommonResponseModel


# Schemas.
class __File(CommonResponseModel):
    """
    File model in the database.
    """

    # Fields.
    project_id_list: list[PyObjectId] = Field(..., description="List of project IDs associated with this file.")
    file_hash: str = Field(..., description="The hash of the file content.")
    filename: str = Field(..., description="The name of the file.")
    file_format: FileFormat = Field(..., description="The format of the file.")
    size_in_bytes: int = Field(..., description="The size of the file in bytes.")


# - Images.
class _ImageFile(__File):
    """
    Schema for an image file.
    """

    # Fields.
    width: int = Field(..., ge=1, description="The width of the image in pixels.")
    height: int = Field(..., ge=1, description="The height of the image in pixels.")
    channels: int = Field(..., ge=1, description="The number of channels in the image.")

    # Validators.
    @field_validator("file_format")
    @classmethod
    def validate_file_format(cls, value: FileFormat) -> FileFormat:
        """
        Validator to ensure the file format is an image format.

        Args:
                value (FileFormat): The file format to validate.

        Returns:
                FileFormat: The validated file format.
        """
        if value not in FileFormat.get_image_formats():
            raise ValueError(
                f"Invalid file format for ImageFile: {value}. Must be one of {FileFormat.get_image_formats()}."
            )
        return value


class ImageFileCreate(_ImageFile, CommonRequestModel):
    """
    Image file creation model.
    """

    pass


class ImageFile(_ImageFile):
    """
    Image file response model.
    """

    pass


# - Texts.
class _TextFile(__File):
    """
    Schema for a text file.
    """

    # Fields.
    number_of_lines: int = Field(..., ge=0, description="The number of lines in the text file.")
    number_of_words: int = Field(..., ge=0, description="The number of words in the text file.")
    number_of_characters: int = Field(..., ge=0, description="The number of characters in the text file.")

    # Validators.
    @field_validator("file_format")
    @classmethod
    def validate_file_format(cls, value: FileFormat) -> FileFormat:
        """
        Validator to ensure the file format is a text format.

        Args:
                value (FileFormat): The file format to validate.

        Returns:
                FileFormat: The validated file format.
        """
        if value not in FileFormat.get_text_formats():
            raise ValueError(
                f"Invalid file format for TextFile: {value}. Must be one of {FileFormat.get_text_formats()}."
            )
        return value


class TextFileCreate(_TextFile, CommonRequestModel):
    """
    Text file creation model.
    """

    pass


class TextFile(_TextFile):
    """
    Text file response model.
    """

    pass


# - Audios.
class _AudioFile(__File):
    """
    Schema for an audio file.
    """

    # Fields.
    duration_in_seconds: float = Field(..., ge=0.5, description="The duration of the audio file in seconds.")
    sample_rate: int = Field(..., ge=1, description="The sample rate of the audio file in Hz.")
    channels: int = Field(..., ge=1, description="The number of channels in the audio file.")

    # Validators.
    @field_validator("file_format")
    @classmethod
    def validate_file_format(cls, value: FileFormat) -> FileFormat:
        """
        Validator to ensure the file format is an audio format.

        Args:
                value (FileFormat): The file format to validate.

        Returns:
                FileFormat: The validated file format.
        """
        if value not in FileFormat.get_audio_formats():
            raise ValueError(
                f"Invalid file format for AudioFile: {value}. Must be one of {FileFormat.get_audio_formats()}."
            )
        return value


class AudioFileCreate(_AudioFile, CommonRequestModel):
    """
    Audio file creation model.
    """

    pass


class AudioFile(_AudioFile):
    """
    Audio file response model.
    """

    pass


# - Multiple Files.
class UploadedFileResponse(CommonModel):
    """
    Response model for uploaded file.
    """

    file_id: PyObjectId | None = Field(default=None, description="The ID of the uploaded file.")
    status: FileUploadStatus = Field(..., description="Status of the uploaded file.")
    message: str = Field(..., description="Message for the uploaded file.")
    size_in_bytes: int | None = Field(default=0, description="The size of the uploaded file in bytes.")


class UploadedFileListResponse(BaseModel):
    """
    Response model for uploaded files.
    """

    data: list[UploadedFileResponse] = Field(..., description="List of uploaded files.")

    @computed_field(description="Total number of created uploaded files.")
    def total_created_uploaded_files(self) -> int:
        """
        Computed field to get the total number of created uploaded files.

        Returns:
                int: The total number of created uploaded files.
        """
        return len([file for file in self.data if file.status == FileUploadStatus.CREATED])

    @computed_field(description="Total size in bytes of uploaded files.")
    def total_size_in_bytes(self) -> int:
        """
        Computed field to get the total size in bytes of uploaded files.

        Returns:
                int: The total size in bytes of uploaded files.
        """
        return int(sum(file.size_in_bytes if file.status == FileUploadStatus.CREATED else 0.0 for file in self.data))  # type: ignore
