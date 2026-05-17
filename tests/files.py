"""
Module used to create temporary files for testing.
"""

import io
import os
import tempfile
import uuid
import wave
from abc import ABC, abstractmethod

import numpy as np
from PIL import Image

from backend.database.enums import FileFormat


# Abstract Classes.
class FileTest(ABC):
    """
    Abstract class used to create temporary files for testing.
    """

    # Special Methods.
    def __init__(self, file_type: FileFormat, filename: str | None = None, **kwargs):
        """
        Initialize the FileTest instance.

        Args:
            file_type (FileFormat): The type of the file to create.
            filename (str | None): The name of the file to create. (Default: None)
        """
        super().__init__()

        if filename is None:
            filename = str(uuid.uuid4())

        # Attributes.
        self.__filename = filename
        self.__file_type = file_type
        self.__temp_file: tempfile._TemporaryFileWrapper | None = None

    def __enter__(self) -> tempfile._TemporaryFileWrapper:
        """
        Create a temporary file and return its name.

        Returns:
            tempfile._TemporaryFileWrapper: The temporary file.
        """
        # Create a temporary file.
        self.__temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{self.__file_type.value}", prefix=self.__filename
        )
        return self.__temp_file

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Delete the temporary file.

        Args:
            exc_type: The type of the exception.
            exc_value: The value of the exception.
            traceback: The traceback of the exception.
        """
        if self.__temp_file:
            self.__temp_file.close()
            os.unlink(self.__temp_file.name)

    # Abstract Methods.
    @staticmethod
    @abstractmethod
    def write_content(*args, **kwargs) -> bytes:
        pass


# Classes.
class TextFileTest(FileTest):
    """
    Class used to create temporary text files for testing.
    """

    # Special Methods.
    def __init__(self, **kwargs):
        """
        Initialize the TextFileTest instance.
        """
        super().__init__(FileFormat.TXT, **kwargs)

    # Static Methods.
    @staticmethod
    def write_content(content: str, encoding: str = "utf-8") -> bytes:
        """
        Write a text content to the file.

        Args:
            content (str): The content to write to the file.
            encoding (str): The encoding to use for the content.

        Returns:
            bytes: The text content as bytes.
        """
        return content.encode(encoding=encoding)


class ImageFileTest(FileTest):
    """
    Class used to create temporary image files for testing.
    """

    # Special Methods.
    def __init__(self, **kwargs):
        """
        Initialize the ImageFileTest instance.
        """
        super().__init__(FileFormat.JPEG, **kwargs)

    # Static Methods.
    @staticmethod
    def write_content(width: int, height: int, channels: int = 3) -> bytes:
        """
        Write a image content to the file.

        Args:
            width (int): The width of the image.
            height (int): The height of the image.
            channels (int): The number of channels in the image.

        Returns:
            bytes: The image content as bytes.
        """
        # Set up image mode.
        if channels == 1:
            mode = "L"
        elif channels == 3:
            mode = "RGB"
        else:
            raise ValueError(f"Unsupported number of channels: {channels}")

        # Create empty image.
        image = Image.new(mode=mode, size=(width, height))

        # Create image buffer.
        buffer = io.BytesIO()
        image.save(fp=buffer, format="JPEG")
        buffer.seek(0)
        return buffer.getvalue()


class AudioFileTest(FileTest):
    """
    Class used to create temporary audio files for testing.
    """

    # Special Methods.
    def __init__(self, **kwargs):
        """
        Initialize the AudioFileTest instance.
        """
        super().__init__(FileFormat.WAV, **kwargs)

    # Static Methods.
    @staticmethod
    def write_content(duration: int, sample_rate: int, channels: int = 1) -> bytes:
        """
        Write a audio content to the file.

        Args:
            duration (int): The duration of the audio in seconds.
            sample_rate (int): The sample rate of the audio.
            channels (int): The number of channels in the audio.

        Returns:
            bytes: The audio content as bytes.
        """
        # Create audio buffer.
        buffer = io.BytesIO()
        with wave.open(f=buffer, mode="wb") as audio_buffer:
            audio_buffer.setnchannels(nchannels=channels)
            audio_buffer.setsampwidth(sampwidth=2)
            audio_buffer.setframerate(framerate=sample_rate)
            signal = (np.random.rand(duration * sample_rate, channels) * 32767).astype(np.int16)
            audio_buffer.writeframes(signal.tobytes())
        buffer.seek(0)
        return buffer.getvalue()
