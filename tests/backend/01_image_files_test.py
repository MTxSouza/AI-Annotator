"""
Module used to test image file-related endpoints.
"""

import io
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tests.backend.conftest import check_for_worker_task_completion


# Mocks.
@pytest.fixture
def corrupt_image_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a corrupt image file payload.
    """
    # Create corrupt image bytes.
    corrupt_image = Image.new("RGB", (100, 100), color=(0, 255, 0))
    buffer = io.BytesIO()
    corrupt_image.save(buffer, format="PNG")

    # Corrupt the image bytes.
    valid_bytes = buffer.getvalue()
    corrupt_bytes = valid_bytes[:10] + b"corrupted_data"

    corrupt_buffer = io.BytesIO(corrupt_bytes)

    return [("file_list", ("corrupt_image.png", corrupt_buffer, "image/png"))]


# Tests.
def test_create_image_file_record(
    client: TestClient,
    object_detection_project_payload: dict,
    list_png_image_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=object_detection_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0

    # Create file record.
    list_png_image_file = list_png_image_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/queue", files=list_png_image_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_png_image_file)

    file_id_list = []
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Created"
        assert file_data["message"] == f"Image file '{list_png_image_file[i][1][0]}' uploaded successfully."
        file_id_list.append(file_data["file_id"])

    # Get project again to check number of files and samples.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project = project_response.json()
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == len(list_png_image_file)
    assert project_details["number_of_samples"] == 0

    # Check file content.
    for i, file_id in enumerate(iterable=file_id_list):
        file_content_response = client.get(url=f"/projects/{project_id}/files/{file_id}/data/")
        assert file_content_response.status_code == 200, f"Failed to get file content: {file_content_response.text}"
        assert file_content_response.content == list_png_image_file[i][1][1].getvalue()


def test_create_duplicate_file_record(
    client: TestClient,
    object_detection_project_payload: dict,
    list_png_image_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a duplicate image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=object_detection_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    list_png_image_file = list_png_image_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/queue", files=list_png_image_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Attempt to create duplicate file record.
    list_png_image_file = list_png_image_file_payload()
    duplicate_file_response = client.post(url=f"/projects/{project_id}/files/queue", files=list_png_image_file)
    assert duplicate_file_response.status_code == 202, (
        f"Failed to create duplicate file: {duplicate_file_response.text}"
    )

    # Wait for the duplicate file processing to complete.
    duplicate_file_response_json = duplicate_file_response.json()
    assert "task_id" in duplicate_file_response_json, "Response does not contain task_id"
    duplicate_file_worker_task_id = duplicate_file_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=duplicate_file_worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_png_image_file)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Skipped"
        assert file_data["message"] == f"File '{list_png_image_file[i][1][0]}' already exists."


def test_create_corrupt_image_file_record(
    client: TestClient,
    object_detection_project_payload: dict,
    corrupt_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a corrupt image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=object_detection_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/queue", files=corrupt_image_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(corrupt_image_file_payload)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == f"Corrupted file: {corrupt_image_file_payload[i][1][0]}."


def test_create_text_file_format_record(
    client: TestClient,
    object_detection_project_payload: dict,
    list_text_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a text file record in an object detection project.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=object_detection_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    list_text_file = list_text_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/queue", files=list_text_file)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_text_file)
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Invalid file format for this project: txt."


def test_create_audio_file_format_record(
    client: TestClient,
    object_detection_project_payload: dict,
    list_wav_audio_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an audio file record in an object detection project.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=object_detection_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    list_wav_audio_file = list_wav_audio_file_payload()
    worker_response = client.post(url=f"/projects/{project_id}/files/queue", files=list_wav_audio_file)
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
