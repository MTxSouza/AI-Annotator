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
        text_content = f"This is test file number {i + 1}."

        # Store text in bytes buffer.
        buffer = io.BytesIO(initial_bytes=text_content.encode("utf-8"))
        buffer.seek(0)

        # Append to list.
        text_file_list.append(("file_list", (f"test_file_{i + 1}.txt", buffer, "text/plain")))

    return text_file_list


# Tests.
def test_create_text_file_record(
    client: TestClient,
    text_project_payload: dict,
    list_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a text file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_project_payload)
    assert project_response.status_code == 201
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    assert project["number_of_files"] == 0
    assert project["number_of_samples"] == 0

    # Create file record.
    file_response = client.post(url=f"/files/{project_id}/", files=list_text_file_payload)
    assert file_response.status_code == 201

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(list_text_file_payload)

    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Created"
        assert file_data["message"] == f"Text file '{list_text_file_payload[i][1][0]}' uploaded successfully."

    # Get project again to check number of files and samples.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200
    project = project_response.json()
    assert project["number_of_files"] == len(list_text_file_payload)
    assert project["number_of_samples"] == 0
