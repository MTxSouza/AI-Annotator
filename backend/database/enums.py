"""
Module with custom types for database operations.
"""

from datetime import datetime
from enum import StrEnum
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
    PlainSerializer(func=lambda oid: str(oid), return_type=str, when_used="json"),
    WithJsonSchema(json_schema={"type": "string"}),
]
PyDateTime = Annotated[datetime, PlainSerializer(func=lambda dt: dt.isoformat())]


class FileUploadStatus(StrEnum):
    """
    Enum for file upload status.
    """

    CREATED = "Created"
    SKIPPED = "Skipped"
    FAILED = "Failed"


class Task(StrEnum):
    """
    Enum for tasks.
    """

    # Image.
    OBJECT_DETECTION = "Object Detection"
    IMAGE_CLASSIFICATION = "Image Classification"
    IMAGE_CAPTION = "Image Caption"
    OBJECT_CAPTION = "Object Caption"

    # Text.
    TEXT_CLASSIFICATION = "Text Classification"
    TEXT_TAGGING = "Text Tagging"

    # Audio.
    AUDIO_CLASSIFICATION = "Audio Classification"
    AUDIO_TRANSCRIPTION = "Audio Transcription"


class FileFormat(StrEnum):
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
            (cls.JPEG, [b"\xff\xd8\xff\xdb", b"\xff\xd8\xff\xe0\00\10\4A\46\49\46\00\01", b"\xff\xd8\xff\xee"]),
            (cls.PNG, [b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"]),
            # Texts.
            (
                cls.TXT,
                [
                    b"\xef\xbb\xbf",  # UTF-8 BOM
                    b"\xff\xfe",  # UTF-16 LE BOM
                    b"\xfe\xff",  # UTF-16 BE BOM
                ],
            ),
            # Audios.
            (cls.WAV, [b"\x52\x49\x46\x46"]),
            (cls.MP3, [b"\x49\x44\x33"]),
        ]

        # Look for matching signatures.
        for file_format, signatures in POSSIBLE_FORMATS:
            for signature in signatures:
                if file_bytes.startswith(signature):
                    return file_format

        # Extra fallback: check if the file is a UTF-8 text file.
        if cls.is_utf8_text(file_bytes=file_bytes):
            return cls.TXT

        return None

    # Static methods.
    @staticmethod
    def is_utf8_text(file_bytes: bytes) -> bool:
        """
        Check if the file bytes represent a UTF-8 text file.

        Args:
            file_bytes (bytes): The file bytes to check.

        Returns:
            bool: True if the file is a UTF-8 text file, False otherwise.
        """
        # Check Null bytes.
        if b"\x00" in file_bytes:
            return False

        # Try decoding the file bytes to check for encoding issues.
        try:
            file_bytes.decode(encoding="utf-8")

        except UnicodeDecodeError:
            return False

        except Exception:
            return False

        return True
