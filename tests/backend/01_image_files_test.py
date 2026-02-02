"""
Module used to test image file-related endpoints.
"""
import io
import shutil

import pytest
from fastapi.testclient import TestClient
from PIL import Image


# Module-wide fixtures.
@pytest.fixture
def reset_file_directory():
    """
    Fixture to reset the file storage directory before each module.
    """
    from backend.api.v1.utils.files import STATIC_FILE_DIRECTORY

    # Reset the static file directory.
    shutil.rmtree(STATIC_FILE_DIRECTORY, ignore_errors=True)

# Mocks.
@pytest.fixture
def project_payload() -> dict:
    """
    Fixture to provide a sample project payload.
    """
    return {
        "name": "Test Project",
        "task": "Object Detection"
    }

@pytest.fixture
def list_image_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a list of image file payloads.
    """
    # Create images.
    IMAGE_SIZE_LIST = [
        (200, 200),
        (300, 150),
        (400, 400),
        (500, 250),
        (600, 300),
        (1280, 720),
        (1920, 1080),
        (3840, 2160)
    ]
    image_file_list = []
    for image_size in IMAGE_SIZE_LIST:
        # Create empty image.
        image = Image.new("RGB", image_size, color=(255, 0, 0))

        # Store image in bytes buffer.
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Append to list.
        image_file_list.append(
            ("file_list", ("test_image_%dx%d.png" % image_size, buffer, "image/png"))
        )

    return image_file_list

@pytest.fixture
def corrupt_image_file_payload() -> tuple[str, tuple[str, io.BytesIO, str]]:
    """
    Fixture to provide a corrupt image file payload.
    """
    # Create corrupt image bytes.
    buffer = io.BytesIO(b"This is not a valid image file.")

    return ("file_list", ("corrupt_image.png", buffer, "image/png"))

# Tests.
def test_create_image_file_record(
    client: TestClient,
    project_payload: dict,
    list_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create an image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url="/files/%s/images/" % project_id, files=list_image_file_payload)
    assert file_response.status_code == 201

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(list_image_file_payload)

    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Created"
        assert file_data["message"] == "Image file '%s' uploaded successfully." % list_image_file_payload[i][1][0]

def test_create_duplicate_file_record(
    client: TestClient,
    project_payload: dict,
    list_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create a duplicate image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url="/files/%s/images/" % project_id, files=list_image_file_payload)
    assert file_response.status_code == 201

    # Attempt to create duplicate file record.
    duplicate_file_response = client.post(url="/files/%s/images/" % project_id, files=list_image_file_payload)
    assert duplicate_file_response.status_code == 201

    # Check response.
    duplicate_file_response_json = duplicate_file_response.json()
    assert "data" in duplicate_file_response_json
    assert len(duplicate_file_response_json["data"]) == len(list_image_file_payload)
    for i, file_data in enumerate(iterable=duplicate_file_response_json["data"]):
        assert file_data["status"] == "Skipped"
        assert file_data["message"] == "File '%s' already exists." % list_image_file_payload[i][1][0]

def test_create_corrupt_image_file_record(
    client: TestClient,
    project_payload: dict,
    corrupt_image_file_payload: tuple[str, tuple[str, io.BytesIO, str]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create a corrupt image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url="/files/%s/images/" % project_id, files=[corrupt_image_file_payload])
    assert file_response.status_code == 201

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == 1

    file_data = file_response_json["data"][0]
    assert file_data["status"] == "Failed"
    assert file_data["message"] == "Corrupted file: %s." % corrupt_image_file_payload[1][0]
