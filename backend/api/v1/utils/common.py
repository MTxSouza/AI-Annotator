"""
Module with all utilities related to common operations, used across different modules to avoid circular
imports.
"""

from pathlib import Path

from fastapi import HTTPException, status

from backend.configs import BackendSettings
from backend.database.enums import PyObjectId


# Functions.
def _load_file_content(filename: str, file_id: str | PyObjectId) -> bytes:
    """
    Utility function to load the content of a file from disk.

    Args:
            filename (str): The filename of the file to load.
            file_id (str | PyObjectId): The ID of the file to load.

    Returns:
            bytes: The content of the file.
    """
    # Load file content from disk.
    file_path = Path(BackendSettings.static_file_directory, filename)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File with ID {file_id} does not exist on disk."
        )
    with file_path.open(mode="rb") as file_buffer:
        content = file_buffer.read()

    return content
