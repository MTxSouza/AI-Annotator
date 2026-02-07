"""
Module used to test image file-related endpoints.
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image


# Mocks.
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

@pytest.fixture
def invalid_file_format_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide an invalid file format payload.
    """
    # Create text file bytes.
    buffer = io.BytesIO(b"This is a text file, not an image.")

    return [("file_list", ("invalid_file.txt", buffer, "text/plain"))]

# Tests.
def test_create_image_file_record(
    client: TestClient,
    image_project_payload: dict,
    list_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create an image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=image_project_payload)
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
    image_project_payload: dict,
    list_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create a duplicate image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=image_project_payload)
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
    image_project_payload: dict,
    corrupt_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create a corrupt image file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=image_project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url="/files/%s/images/" % project_id, files=corrupt_image_file_payload)
    assert file_response.status_code == 201

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(corrupt_image_file_payload)
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Corrupted file: %s." % corrupt_image_file_payload[i][1][0]

def test_create_invalid_file_format_record(
    client: TestClient,
    image_project_payload: dict,
    invalid_file_format_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None  # Used to reset file directory
    ):
    """
    Test to create an invalid file format record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=image_project_payload)
    assert project_response.status_code == 201
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url="/files/%s/images/" % project_id, files=invalid_file_format_payload)
    assert file_response.status_code == 201

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(invalid_file_format_payload)
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Invalid file format for this project: txt."
