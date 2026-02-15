"""
Module used to test object detection sample-related endpoints.
"""

import io
import random

import bson
import pytest
from fastapi.testclient import TestClient
from PIL import Image


# Mocks.
@pytest.fixture
def image_file_payload() -> list[tuple[str, tuple[str, bytes, str]]]:
    """
    Fixture to provide an image file payload.
    """
    # Create empty image.
    image = Image.new("RGB", (448, 448), color=(255, 0, 0))

    # Store image in bytes buffer.
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return [("file_list", ("test_image.png", buffer.getvalue(), "image/png"))]


@pytest.fixture
def list_object_detection_sample_payload() -> tuple[list[dict], list[str]]:
    """
    Fixture to provide a list of object detection sample payloads.
    """
    # Create samples.
    number_of_samples = 10
    class_name_list = [f"class_{i}" for i in range(number_of_samples)]
    sample_class_name_list = []
    sample_list = []
    for i in range(number_of_samples):
        # Set random class name.
        class_name = random.choice(class_name_list)

        # Set random coordinates and dimensions.
        cx = random.uniform(0.0, 1.0)
        cy = random.uniform(0.0, 1.0)
        width = random.uniform(0.0, 1.0)
        height = random.uniform(0.0, 1.0)

        # Append to list.
        sample_list.append(
            {
                "class_name": class_name,
                "cx": cx,
                "cy": cy,
                "width": width,
                "height": height,
            }
        )
        sample_class_name_list.append(class_name)

    return sample_list, sample_class_name_list


# Tests.
def test_create_object_detection_sample(
    client: TestClient,
    image_project_payload: dict,
    image_file_payload: list[tuple[str, tuple[str, bytes, str]]],
    list_object_detection_sample_payload: tuple[list[dict], list[str]],
    reset_file_directory: None,  # Used to reset file directory
) -> None:
    """
    Test to create an object detection sample.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=image_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    file_response = client.post(url=f"/files/{project_id}/", files=image_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"
    file_list = file_response.json()["data"]
    assert len(file_list) == 1
    file_id = file_list.pop()["file_id"]

    # Set sample payload.
    sample_list, sample_class_name_list = list_object_detection_sample_payload
    for sample in sample_list:
        sample["project_id"] = project_id
        sample["file_id"] = file_id

        # Create sample.
        sample_response = client.post(url=f"/samples/{project_id}/", json=sample)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"
        sample_data = sample_response.json()

        # Check response.
        assert sample_data["project_id"] == project_id
        assert sample_data["file_id"] == file_id
        assert sample_data["class_name"] == sample["class_name"]
        assert sample_data["cx"] == sample["cx"]
        assert sample_data["cy"] == sample["cy"]
        assert sample_data["width"] == sample["width"]
        assert sample_data["height"] == sample["height"]

    # Get project again to check extra informations.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project = project_response.json()
    assert project["number_of_files"] == 1
    assert project["number_of_samples"] == len(sample_list)

    project_config = project["configs"]
    assert set(project_config["class_name_list"]) == set(sample_class_name_list)


def test_create_object_detection_sample_with_nonexistent_file(
    client: TestClient,
    image_project_payload: dict,
    list_object_detection_sample_payload: tuple[list[dict], list[str]],
    reset_file_directory: None,  # Used to reset file directory
) -> None:
    """
    Test to create an object detection sample with a non-existent file.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=image_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Set sample payload.
    sample_list, _ = list_object_detection_sample_payload
    for sample in sample_list:
        sample["project_id"] = project_id
        sample["file_id"] = str(bson.ObjectId())  # Set non-existent file ID.

        # Create sample.
        sample_response = client.post(url=f"/samples/{project_id}/", json=sample)
        assert sample_response.status_code == 404, (
            f"Failed to not create sample with non-existent file: {sample_response.text}"
        )
        assert sample_response.json()["detail"] == f"File with ID {sample['file_id']} does not exist."
