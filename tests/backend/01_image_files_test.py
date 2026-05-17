"""
Module used to test image file-related endpoints.
"""

# Imports.
from pathlib import Path

from fastapi.testclient import TestClient

from tests.backend.conftest import check_for_worker_task_completion
from tests.files import ImageFileTest


# Tests.
def test_insert_image_file_to_project(
    client: TestClient, object_detection_project_payload: dict, image_200x200_payload: bytes
) -> None:
    """
    Test inserting an image file into an object detection project.
    """
    # Create a new project.
    response = client.post("/projects", json=object_detection_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    assert project_response["name"] == object_detection_project_payload["name"], "Project name does not match payload"
    assert project_response["task"] == object_detection_project_payload["task"], "Project task does not match payload"
    assert project_response["description"] is None, "Project description should be None"
    assert project_response["is_private"] is False, "Project should not be private"

    # Insert an image file into the project.
    project_id = project_response["_id"]
    with ImageFileTest() as image_filepath:
        image_filepath_name = Path(image_filepath.name).name
        image_filepath.write(image_200x200_payload)
        image_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": image_filepath.name})
        assert worker_response.status_code == 202, f"Failed to insert image file into project: {worker_response.text}"

        # Wait for the file processing to complete.
        worker_response_json = worker_response.json()
        assert "task_id" in worker_response_json, "Response does not contain task_id"
        worker_task_id = worker_response_json["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        # Check response.
        assert len(file_data_list) == 1, f"Expected 1 file to be processed, but got {len(file_data_list)}"

        file_id_list = []
        for _, file_data in enumerate(iterable=file_data_list):
            assert file_data["status"] == "Created", file_data["message"]
            assert file_data["message"] == f"Image file '{image_filepath_name}' uploaded successfully."
            file_id_list.append(file_data["file_id"])

        # Get project again to check number of files and samples.
        project_response = client.get(url=f"/projects/{project_id}/")
        assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
        project = project_response.json()
        project_details = project.get("details", {})
        assert project_details["number_of_files"] == 1
        assert project_details["number_of_samples"] == 0

        # Check file content.
        for _, file_id in enumerate(iterable=file_id_list):
            file_content_response = client.get(url=f"/projects/{project_id}/files/{file_id}/data/")
            assert file_content_response.status_code == 200, f"Failed to get file content: {file_content_response.text}"
            assert file_content_response.content == image_200x200_payload, (
                "File content does not match original content"
            )


def test_insert_duplicate_image_file_to_project(
    client: TestClient, object_detection_project_payload: dict, image_200x200_payload: bytes
) -> None:
    """
    Test inserting a duplicate image file into an object detection project.
    """
    # Create a new project.
    response = client.post("/projects", json=object_detection_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert an image file into the project.
    with ImageFileTest() as image_filepath:
        image_filepath_name = Path(image_filepath.name).name
        image_filepath.write(image_200x200_payload)
        image_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": image_filepath.name})
        assert worker_response.status_code == 202, f"Failed to insert image file into project: {worker_response.text}"

        # Wait for the file processing to complete.
        worker_response_json = worker_response.json()
        assert "task_id" in worker_response_json, "Response does not contain task_id"
        worker_task_id = worker_response_json["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        # Check response.
        assert len(file_data_list) == 1, f"Expected 1 file to be processed, but got {len(file_data_list)}"

        for _, file_data in enumerate(iterable=file_data_list):
            assert file_data["status"] == "Created", file_data["message"]
            assert file_data["message"] == f"Image file '{image_filepath_name}' uploaded successfully."

        # Insert the same file again.
        duplicate_worker_response = client.post(
            f"/projects/{project_id}/files", params={"filepath": image_filepath.name}
        )
        assert duplicate_worker_response.status_code == 202, (
            f"Expected 202 status code for duplicate file insertion, but got {duplicate_worker_response.status_code}"
        )

        # Wait for the file processing to complete.
        duplicated_worker_response_json = duplicate_worker_response.json()
        assert "task_id" in duplicated_worker_response_json, "Response does not contain task_id"
        worker_task_id = duplicated_worker_response_json["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        # Check response.
        assert len(file_data_list) == 1, f"Expected 1 file to be processed, but got {len(file_data_list)}"

        for _, file_data in enumerate(iterable=file_data_list):
            assert file_data["status"] == "Skipped", file_data["message"]
            assert file_data["message"] == f"File '{image_filepath_name}' already exists."

        # Get project again to check number of files and samples.
        project_response = client.get(url=f"/projects/{project_id}/")
        assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
        project = project_response.json()
        project_details = project.get("details", {})
        assert project_details["number_of_files"] == 1
        assert project_details["number_of_samples"] == 0


def test_insert_corrupt_image_file_to_project(client: TestClient, object_detection_project_payload: dict) -> None:
    """
    Test inserting a corrupt image file into an object detection project.
    """
    # Create a new project.
    response = client.post("/projects", json=object_detection_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert a corrupt image file into the project.
    with ImageFileTest() as image_filepath:
        image_filepath_name = Path(image_filepath.name).name
        # Write invalid JPEG bytes to the file.
        image_filepath.write(b"\xff\xd8\xff\xdb\x00\x00\x00\x00")
        image_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": image_filepath.name})
        assert worker_response.status_code == 202, (
            f"Failed to insert corrupt image file into project: {worker_response.text}"
        )

        # Wait for the file processing to complete.
        worker_response_json = worker_response.json()
        assert "task_id" in worker_response_json, "Response does not contain task_id"
        worker_task_id = worker_response_json["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        # Check response.
        assert len(file_data_list) == 1, f"Expected 1 file to be processed, but got {len(file_data_list)}"

        for _, file_data in enumerate(iterable=file_data_list):
            assert file_data["status"] == "Failed", file_data["message"]
            assert file_data["message"] == f"Corrupted file: {image_filepath_name}."

        # Get project again to check number of files and samples.
        project_response = client.get(url=f"/projects/{project_id}/")
        assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
        project = project_response.json()
        project_details = project.get("details", {})
        assert project_details["number_of_files"] == 0
        assert project_details["number_of_samples"] == 0


def test_insert_multiple_image_files_to_project(
    client: TestClient,
    object_detection_project_payload: dict,
    image_200x200_payload: bytes,
    image_300x300_payload: bytes,
) -> None:
    """
    Test inserting multiple image files into an object detection project.
    """
    # Create a new project.
    response = client.post("/projects", json=object_detection_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert multiple image files into the project.
    with ImageFileTest() as image_filepath_1, ImageFileTest() as image_filepath_2:
        image_filepath_1.write(image_200x200_payload)
        image_filepath_1.flush()

        image_filepath_2.write(image_300x300_payload)
        image_filepath_2.flush()

        worker_response = client.post(
            f"/projects/{project_id}/files", params={"filepath": [image_filepath_1.name, image_filepath_2.name]}
        )
        assert worker_response.status_code == 202, (
            f"Failed to insert multiple image files into project: {worker_response.text}"
        )

        # Wait for the file processing to complete.
        worker_response_json = worker_response.json()
        assert "task_id" in worker_response_json, "Response does not contain task_id"
        worker_task_id = worker_response_json["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        # Check response.
        assert len(file_data_list) == 2, f"Expected 2 files to be processed, but got {len(file_data_list)}"

        for _, file_data in enumerate(iterable=file_data_list):
            assert file_data["status"] == "Created", file_data["message"]

        # Get project again to check number of files and samples.
        project_response = client.get(url=f"/projects/{project_id}/")
        assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
        project = project_response.json()
        project_details = project.get("details", {})
        assert project_details["number_of_files"] == 2
        assert project_details["number_of_samples"] == 0


def test_delete_image_file_from_project(
    client: TestClient, object_detection_project_payload: dict, image_200x200_payload: bytes
) -> None:
    """
    Test deleting an image file from an object detection project.
    """
    # Create a new project.
    response = client.post("/projects", json=object_detection_project_payload)

    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert an image file into the project.
    with ImageFileTest() as image_filepath:
        image_filepath.write(image_200x200_payload)
        image_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": image_filepath.name})
        assert worker_response.status_code == 202, f"Failed to insert image file into project: {worker_response.text}"

        worker_task_id = worker_response.json()["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        assert len(file_data_list) == 1
        assert file_data_list[0]["status"] == "Created", file_data_list[0]["message"]
        file_id = file_data_list[0]["file_id"]

    # Delete the file from the project.
    delete_response = client.delete(url=f"/projects/{project_id}/files/{file_id}")
    assert delete_response.status_code == 204, f"Failed to delete image file from project: {delete_response.text}"

    # Verify the file is no longer accessible in the project.
    file_content_response = client.get(url=f"/projects/{project_id}/files/{file_id}/data/")
    assert file_content_response.status_code == 404, "File should not be accessible after deletion"

    # Verify the project no longer has the file.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project_details = project_response.json().get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0
