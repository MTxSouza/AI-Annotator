"""
Module used to test text file-related endpoints.
"""

import io

import pytest
from fastapi.testclient import TestClient


# Mocks.
@pytest.fixture
def corrupt_text_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a corrupt text file payload.
    """
    # Create corrupt text content.
    valid_uft8_bom = b"\xef\xbb\xbf"
    invalid_content = b"Corrupted file -> \xff\xfe\x00\x00"
    corrupt_content_bytes = valid_uft8_bom + invalid_content

    # Store corrupt text in bytes buffer.
    buffer = io.BytesIO(initial_bytes=corrupt_content_bytes)
    buffer.seek(0)

    return [("file_list", ("corrupt_file.txt", buffer, "text/plain"))]


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
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    assert project["number_of_files"] == 0
    assert project["number_of_samples"] == 0

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=list_text_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(list_text_file_payload)

    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Created"
        assert file_data["message"] == f"Text file '{list_text_file_payload[i][1][0]}' uploaded successfully."

    # Get project again to check number of files and samples.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project = project_response.json()
    assert project["number_of_files"] == len(list_text_file_payload)
    assert project["number_of_samples"] == 0
    assert not project["details"]["class_name_list"]


def test_create_duplicate_text_file_record(
    client: TestClient,
    text_project_payload: dict,
    list_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a duplicate text file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    assert project["number_of_files"] == 0
    assert project["number_of_samples"] == 0

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=list_text_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Attempt to create duplicate file record.
    duplicate_file_response = client.post(url=f"/projects/{project_id}/files/", files=list_text_file_payload)
    assert duplicate_file_response.status_code == 201, (
        f"Failed to create duplicate file: {duplicate_file_response.text}"
    )

    # Check response.
    duplicate_file_response_json = duplicate_file_response.json()
    assert "data" in duplicate_file_response_json
    assert len(duplicate_file_response_json["data"]) == len(list_text_file_payload)
    for i, file_data in enumerate(iterable=duplicate_file_response_json["data"]):
        assert file_data["status"] == "Skipped"
        assert file_data["message"] == f"File '{list_text_file_payload[i][1][0]}' already exists."


def test_create_corrupt_text_file_record(
    client: TestClient,
    text_project_payload: dict,
    corrupt_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a corrupt text file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=corrupt_text_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(corrupt_text_file_payload)
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == f"Corrupted file: {corrupt_text_file_payload[i][1][0]}."
