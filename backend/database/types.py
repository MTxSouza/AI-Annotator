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

    @classmethod
    def _check_file_format(cls, file_bytes: bytes) -> "FileFormat | None":
        """
        Check the file format based on the file bytes.

        Args:
            file_bytes (bytes): The file bytes to check.

        Returns:
            FileFormat | None: The detected file format or None if not detected.
        """
        # Determine possible formats.
        POSSIBLE_FORMATS = [
            # Images.
            (cls.JPEG, [
                b"\xFF\xD8\xFF\xDB",
                b"\xFF\xD8\xFF\xE0\00\10\4A\46\49\46\00\01",
                b"\xFF\xD8\xFF\xEE"
            ]),
            (cls.PNG, [b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"]),
            # Texts.
            (cls.TXT, [
                b"",
                b"\xEF\xBB\xBF",        # UTF-8 BOM
                b"\xFF\xFE",            # UTF-16 LE BOM
                b"\xFE\xFF",            # UTF-16 BE BOM
                b"\xFF\xFE\x00\x00",    # UTF-32 LE BOM
                b"\x00\x00\xFE\xFF",    # UTF-32 BE BOM,
                b"\x0E\xFE\xFF"         # UTF-7 BOM
            ]),
            # Audios.
            (cls.WAV, [b"\x52\x49\x46\x46"]),
            (cls.MP3, [b"\x49\x44\x33"])
        ]

        # Look for matching signatures.
        for file_format, signatures in POSSIBLE_FORMATS:
            for signature in signatures:
                if file_bytes.startswith(signature):
                    return file_format
        return None
