"""
Module used to test text file-related endpoints.
"""
import io

import pytest
from fastapi.testclient import TestClient


# Mocks.
@pytest.fixture
def list_text_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a list of text file payloads.
    """
    # Create text files.
    text_file_list = []
    for i in range(5):
        # Create text content.
        text_content = "This is test file number %d." % (i + 1)

        # Store text in bytes buffer.
        buffer = io.BytesIO(initial_bytes=text_content.encode("utf-8"))
        buffer.seek(0)

        # Append to list.
        text_file_list.append(
            ("file_list", ("test_file_%d.txt" % (i + 1), buffer, "text/plain"))
        )

    return text_file_list

# Tests.
def test_create_text_file_record(
    client: TestClient,
    list_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory  
    ):
    """
    Test to create a text file record.
    """
    # (TODO: IMPLMENTATION GOES HERE. THERE IS NO TASK AVAILABLE FOR TEXT FILES YET)
    pass
