"""
Module with all utilities related to common operations, used across different modules to avoid circular
imports.
"""

from pathlib import Path

from fastapi import HTTPException, status


# Functions.
def _load_file_content(filepath: str) -> bytes:
    """
    Utility function to load the content of a file from disk.

    Args:
            filepath (str): The path of the file to load.

    Returns:
            bytes: The content of the file.
    """
    # Load file content from disk.
    file_path = Path(filepath)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File path {filepath} does not exist on disk."
        )
    with file_path.open(mode="rb") as file_buffer:
        content = file_buffer.read()

    return content
