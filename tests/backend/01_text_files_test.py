"""
Module used to test text file-related endpoints.
"""

# Imports.
from pathlib import Path

from fastapi.testclient import TestClient

from tests.backend.conftest import check_for_worker_task_completion
from tests.files import TextFileTest


# Tests.
def test_insert_text_file_to_project(
    client: TestClient, text_classification_project_payload: dict, text_100words_payload: bytes
) -> None:
    """
    Test inserting a text file into a text classification project.
    """
    # Create a new project.
    response = client.post("/projects", json=text_classification_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    assert project_response["name"] == text_classification_project_payload["name"], (
        "Project name does not match payload"
    )
    assert project_response["task"] == text_classification_project_payload["task"], (
        "Project task does not match payload"
    )
    assert project_response["description"] is None, "Project description should be None"
    assert project_response["is_private"] is False, "Project should not be private"

    # Insert a text file into the project.
    project_id = project_response["_id"]
    with TextFileTest() as text_filepath:
        text_filepath_name = Path(text_filepath.name).name
        text_filepath.write(text_100words_payload)
        text_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": text_filepath.name})
        assert worker_response.status_code == 202, f"Failed to insert text file into project: {worker_response.text}"

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
            assert file_data["message"] == f"Text file '{text_filepath_name}' uploaded successfully."
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
            assert file_content_response.content == text_100words_payload, (
                "File content does not match original content"
            )


def test_insert_duplicate_text_file_to_project(
    client: TestClient, text_classification_project_payload: dict, text_100words_payload: bytes
) -> None:
    """
    Test inserting a duplicate text file into a text classification project.
    """
    # Create a new project.
    response = client.post("/projects", json=text_classification_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert a text file into the project.
    with TextFileTest() as text_filepath:
        text_filepath_name = Path(text_filepath.name).name
        text_filepath.write(text_100words_payload)
        text_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": text_filepath.name})
        assert worker_response.status_code == 202, f"Failed to insert text file into project: {worker_response.text}"

        # Wait for the file processing to complete.
        worker_response_json = worker_response.json()
        assert "task_id" in worker_response_json, "Response does not contain task_id"
        worker_task_id = worker_response_json["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        # Check response.
        assert len(file_data_list) == 1, f"Expected 1 file to be processed, but got {len(file_data_list)}"

        for _, file_data in enumerate(iterable=file_data_list):
            assert file_data["status"] == "Created", file_data["message"]
            assert file_data["message"] == f"Text file '{text_filepath_name}' uploaded successfully."

        # Insert the same file again.
        duplicate_worker_response = client.post(
            f"/projects/{project_id}/files", params={"filepath": text_filepath.name}
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
            assert file_data["message"] == f"File '{text_filepath_name}' already exists."

        # Get project again to check number of files and samples.
        project_response = client.get(url=f"/projects/{project_id}/")
        assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
        project = project_response.json()
        project_details = project.get("details", {})
        assert project_details["number_of_files"] == 1
        assert project_details["number_of_samples"] == 0


def test_insert_corrupt_text_file_to_project(client: TestClient, text_classification_project_payload: dict) -> None:
    """
    Test inserting a corrupt text file into a text classification project.
    """
    # Create a new project.
    response = client.post("/projects", json=text_classification_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert a corrupt text file into the project.
    with TextFileTest() as text_filepath:
        text_filepath_name = Path(text_filepath.name).name
        # Write invalid UTF-8 bytes to the file.
        text_filepath.write(b"\xff\xfe\xfa\xfb")
        text_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": text_filepath.name})
        assert worker_response.status_code == 202, (
            f"Failed to insert corrupt text file into project: {worker_response.text}"
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
            assert file_data["message"] == f"Corrupted file: {text_filepath_name}."

        # Get project again to check number of files and samples.
        project_response = client.get(url=f"/projects/{project_id}/")
        assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
        project = project_response.json()
        project_details = project.get("details", {})
        assert project_details["number_of_files"] == 0
        assert project_details["number_of_samples"] == 0


def test_insert_multiple_text_files_to_project(
    client: TestClient,
    text_classification_project_payload: dict,
    text_100words_payload: bytes,
    text_1000words_payload: bytes,
) -> None:
    """
    Test inserting multiple text files into a text classification project.
    """
    # Create a new project.
    response = client.post("/projects", json=text_classification_project_payload)

    # Assert that the project was created successfully.
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert multiple text files into the project.
    with TextFileTest() as text_filepath_1, TextFileTest() as text_filepath_2:
        text_filepath_1.write(text_100words_payload)
        text_filepath_1.flush()

        text_filepath_2.write(text_1000words_payload)
        text_filepath_2.flush()

        worker_response = client.post(
            f"/projects/{project_id}/files", params={"filepath": [text_filepath_1.name, text_filepath_2.name]}
        )
        assert worker_response.status_code == 202, (
            f"Failed to insert multiple text files into project: {worker_response.text}"
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


def test_delete_text_file_from_project(
    client: TestClient, text_classification_project_payload: dict, text_100words_payload: bytes
) -> None:
    """
    Test deleting a text file from a text classification project.
    """
    # Create a new project.
    response = client.post("/projects", json=text_classification_project_payload)

    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_response = response.json()
    project_id = project_response["_id"]

    # Insert a text file into the project.
    with TextFileTest() as text_filepath:
        text_filepath.write(text_100words_payload)
        text_filepath.flush()
        worker_response = client.post(f"/projects/{project_id}/files", params={"filepath": text_filepath.name})
        assert worker_response.status_code == 202, f"Failed to insert text file into project: {worker_response.text}"

        worker_task_id = worker_response.json()["task_id"]
        file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

        assert len(file_data_list) == 1
        assert file_data_list[0]["status"] == "Created", file_data_list[0]["message"]
        file_id = file_data_list[0]["file_id"]

    # Delete the file from the project.
    delete_response = client.delete(url=f"/projects/{project_id}/files/{file_id}")
    assert delete_response.status_code == 204, f"Failed to delete text file from project: {delete_response.text}"

    # Verify the file is no longer accessible in the project.
    file_content_response = client.get(url=f"/projects/{project_id}/files/{file_id}/data/")
    assert file_content_response.status_code == 404, "File should not be accessible after deletion"

    # Verify the project no longer has the file.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project_details = project_response.json().get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0
