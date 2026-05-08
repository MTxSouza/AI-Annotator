"""
Module used to test text file-related endpoints.
"""

import io
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from backend.configs import BackendSettings
from tests.backend.conftest import check_for_worker_task_completion


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


@pytest.fixture
def larger_than_maximum_text_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a text file payload that exceeds the maximum file size limit.
    """
    # Create text content that exceeds the maximum file size limit.
    large_text_content = b"A" * (
        BackendSettings.max_upload_file_size + 1
    )  # Create bytes that are 1 byte larger than the limit

    # Write the text content to a bytes buffer.
    text_buffer = io.BytesIO(initial_bytes=large_text_content)
    text_buffer.seek(0)

    return [("file_list", ("large_text_file.txt", text_buffer, "text/plain"))]


# Tests.
def test_create_text_file_record(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a text file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0

    # Create file record.
    list_text_file = list_text_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=list_text_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_text_file)
    file_id_list = []
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Created"
        assert file_data["message"] == f"Text file '{list_text_file[i][1][0]}' uploaded successfully."
        file_id_list.append(file_data["file_id"])

    # Get project again to check number of files and samples.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project = project_response.json()
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == len(list_text_file)
    assert project_details["number_of_samples"] == 0
    assert not project_details["class_name_list"]

    # Check file content.
    for i, file_id in enumerate(iterable=file_id_list):
        file_content_response = client.get(url=f"/projects/{project_id}/files/{file_id}/data/")
        assert file_content_response.status_code == 200, f"Failed to get file content: {file_content_response.text}"
        assert file_content_response.text == list_text_file[i][1][1].getvalue().decode("utf-8")


def test_create_duplicate_text_file_record(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a duplicate text file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0

    # Create file record.
    file_text_file = list_text_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=file_text_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Attempt to create duplicate file record.
    file_text_file = list_text_file_payload()
    duplicate_file_response = client.post(url=f"/projects/{project_id}/files/", files=file_text_file)
    assert duplicate_file_response.status_code == 202, (
        f"Failed to create duplicate file: {duplicate_file_response.text}"
    )

    # Wait for the duplicate file processing to complete.
    duplicate_worker_response_json = duplicate_file_response.json()
    assert "task_id" in duplicate_worker_response_json, "Response does not contain task_id"
    duplicate_worker_task_id = duplicate_worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=duplicate_worker_task_id)

    # Check response.
    assert len(file_data_list) == len(file_text_file)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Skipped"
        assert file_data["message"] == f"File '{file_text_file[i][1][0]}' already exists."


def test_create_corrupt_text_file_record(
    client: TestClient,
    text_classification_project_payload: dict,
    corrupt_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a corrupt text file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=corrupt_text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(corrupt_text_file_payload)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == f"Corrupted file: {corrupt_text_file_payload[i][1][0]}."


def test_create_image_file_format_record(
    client: TestClient,
    text_classification_project_payload: dict,
    list_png_image_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an image file record in a text classification project.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    list_png_image_file = list_png_image_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=list_png_image_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_png_image_file)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Invalid file format for this project: png."


def test_create_audio_file_format_record(
    client: TestClient,
    text_classification_project_payload: dict,
    list_wav_audio_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an audio file record in a text classification project.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    list_wav_audio_file = list_wav_audio_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=list_wav_audio_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_wav_audio_file)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Invalid file format for this project: wav."


def test_upload_maximum_text_file_size_limit(
    client: TestClient,
    text_classification_project_payload: dict,
    larger_than_maximum_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to check uploading a text file that exceeds the maximum file size limit.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=larger_than_maximum_text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(larger_than_maximum_text_file_payload)
    for i, file_data in enumerate(iterable=file_data_list):
        text_filename = larger_than_maximum_text_file_payload[i][1][0]
        assert file_data["status"] == "Failed"
        assert file_data["message"] == f"File '{text_filename}' upload failed: Upload size limit exceeded."
