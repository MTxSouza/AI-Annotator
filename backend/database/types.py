"""
Module with custom types for database operations.
"""
from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema


# Types.
def validate_py_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(oid=v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(func=validate_py_object_id),
    PlainSerializer(func=lambda oid: str(oid), return_type=str),
    WithJsonSchema(json_schema={"type": "string"})
]
PyDateTime = Annotated[datetime, PlainSerializer(func=lambda dt: dt.isoformat())]

class FileUploadStatus(str, Enum):
    """
    Enum for file upload status.
    """
    CREATED = "Created"
    SKIPPED = "Skipped"
    FAILED = "Failed"

class Task(str, Enum):
    """
    Enum for tasks.
    """
    OBJECT_DETECTION = "Object Detection"
    SEMANTIC_SEGMENTATION = "Semantic Segmentation"

class FileFormat(str, Enum):
    """
    Enum for image file formats.
    """
    # Images.
    JPEG = "jpeg"
    PNG = "png"

    # Texts.
    TXT = "txt"

    # Audios.
    WAV = "wav"
    MP3 = "mp3"

    # Class methods.
    @classmethod
    def get_image_formats(cls) -> list["FileFormat"]:
        """
        Get all image file formats.

        Returns:
            list[FileFormat]: List of all image file formats.
        """
        return [cls.JPEG, cls.PNG]

    @classmethod
    def get_text_formats(cls) -> list["FileFormat"]:
        """
        Get all text file formats.

        Returns:
            list[FileFormat]: List of all text file formats.
        """
        return [cls.TXT]

    @classmethod
    def get_audio_formats(cls) -> list["FileFormat"]:
        """
        Get all audio file formats.

        Returns:
            list[FileFormat]: List of all audio file formats.
        """
        return [cls.WAV, cls.MP3]
