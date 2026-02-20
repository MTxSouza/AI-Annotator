"""
Module used to test text classification sample-related endpoints.
"""

import bson
import pytest
from fastapi.testclient import TestClient

from tests.backend.conftest import check_for_worker_task_completion


# Mocks.
@pytest.fixture
def list_text_classification_sample_payload() -> tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]]:
    """
    Fixture to provide a list files and it classes for text classification sample payload.
    """
    # Set mock text.
    file_text_content_list = [
        "This is a neutral statement.",
        "I love this product! It's amazing.",
        "This is the worst experience I've ever had.",
    ]
    file_class_list = ["Neutral", "Positive", "Negative"]

    # Create files and set it classes.
    file_payload_list = []
    sample_class_list = []
    for i, text_content in enumerate(file_text_content_list):
        file_data = [("file_list", (f"file_{i}.txt", text_content.encode("utf-8"), "text/plain"))]
        file_class = file_class_list[i]
        file_payload_list.append(file_data[0])
        sample_class_list.append(file_class)

    return file_payload_list, sample_class_list


# Tests.
def test_create_text_classification_sample(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a text classification sample.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

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
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID and text content from response.
    assert len(file_data_list) == len(text_file_payload)

    file_id_list = []
    file_content_list = []
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Created"
        file_id_list.append(file_data["file_id"])
        file_content_list.append(text_file_payload[i][1][1].decode(encoding="utf-8"))

    # Set sample payload.
    for i, sample_class in enumerate(iterable=sample_class_list):
        sample_payload = {"project_id": project_id, "file_id": file_id_list[i], "class_name": sample_class}

        # Create sample record.
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"

        # Check response.
        sample_response_json = sample_response.json()
        assert sample_response_json["class_name"] == sample_class
        assert sample_response_json["text"] == file_content_list[i]


def test_create_more_than_one_text_classification_sample_per_file(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create more than one text classification sample for a file.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    single_text_file_payload = [text_file_payload[0]]
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=single_text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID and text content from response.
    assert len(file_data_list) == 1
    file_id = file_data_list[0]["file_id"]

    # Set sample payload.
    sample_payload = {"project_id": project_id, "file_id": file_id, "class_name": sample_class_list[0]}
    sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
    assert sample_response.status_code == 201, f"Failed to create first sample: {sample_response.text}"

    # Set second sample payload with same file ID.
    second_sample_payload = {"project_id": project_id, "file_id": file_id, "class_name": sample_class_list[1]}
    second_sample_response = client.post(url=f"/projects/{project_id}/samples/", json=second_sample_payload)
    assert second_sample_response.status_code == 400, (
        f"Failed to not create second sample with same file ID: {second_sample_response.text}"
    )
    assert (
        second_sample_response.json()["detail"]
        == f"Number of samples for file with ID {file_id} for the task Text Classification cannot exceed 1."
    )


def test_create_text_classification_sample_with_nonexistent_file(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a text classification sample with a non-existent file.
    """
    # Unpack payload.
    _, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Set sample payload with non-existent file ID.
    sample = {
        "project_id": project_id,
        "file_id": str(bson.ObjectId()),  # Set non-existent file ID.
        "class_name": sample_class_list[0],
    }

    # Attempt to create sample record.
    sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample)
    assert sample_response.status_code == 404, (
        f"Failed to not create sample with non-existent file: {sample_response.text}"
    )
    assert sample_response.json()["detail"] == f"File with ID {sample['file_id']} does not exist."


def test_update_text_classification_sample(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to update a text classification sample.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(text_file_payload)

    # Get file ID and text content from response.
    file_id_list = []
    file_content_list = []
    for i, file_data in enumerate(iterable=file_data_list):
        assert file_data["status"] == "Created"
        file_id_list.append(file_data["file_id"])
        file_content_list.append(text_file_payload[i][1][1].decode(encoding="utf-8"))

    # Set sample payload.
    for i, sample_class in enumerate(iterable=sample_class_list):
        sample_payload = {"project_id": project_id, "file_id": file_id_list[i], "class_name": sample_class}

        # Create sample record.
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"

        # Get sample ID from response.
        sample_response_json = sample_response.json()
        sample_id = sample_response_json["_id"]

        # Update class of sample record.
        updated_class_name = f"{sample_class} - Updated"
        update_payload = {"class_name": updated_class_name}

        update_response = client.put(url=f"/projects/{project_id}/samples/{sample_id}", json=update_payload)
        assert update_response.status_code == 201, f"Failed to update sample: {update_response.text}"

        # Check response.
        update_response_json = update_response.json()
        assert update_response_json["class_name"] == updated_class_name
        assert update_response_json["text"] == file_content_list[i]

        # Update text of sample record.
        updated_text = f"{file_content_list[i]} - Updated"
        update_payload = {"text": updated_text}

        update_response = client.put(url=f"/projects/{project_id}/samples/{sample_id}", json=update_payload)
        assert update_response.status_code == 201, f"Failed to update sample text: {update_response.text}"

        # Check response.
        update_response_json = update_response.json()
        assert update_response_json["class_name"] == updated_class_name
        assert update_response_json["text"] == updated_text


def test_update_text_classification_sample_with_wrong_project_id(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to update a text classification sample with wrong project ID.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create second project to get its ID.
    second_text_project_payload = text_classification_project_payload.copy()
    second_text_project_payload["name"] = "Second Text Classification Project"
    second_project_response = client.post(url="/projects/", json=second_text_project_payload)
    assert second_project_response.status_code == 201, (
        f"Failed to create second project: {second_project_response.text}"
    )
    second_project = second_project_response.json()
    second_project_id = second_project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID from response.
    assert len(file_data_list) == len(text_file_payload)
    file_id_list = []
    for file_data in file_data_list:
        assert file_data["status"] == "Created"
        file_id_list.append(file_data["file_id"])

    # Set sample payload.
    for i, sample_class in enumerate(iterable=sample_class_list):
        sample_payload = {"project_id": project_id, "file_id": file_id_list[i], "class_name": sample_class}

        # Create sample record.
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"

        # Get sample ID from response.
        sample_response_json = sample_response.json()
        sample_id = sample_response_json["_id"]

        # Attempt to update sample record with wrong project ID.
        update_payload = {"class_name": f"{sample_class} - Updated"}

        update_response = client.put(url=f"/projects/{second_project_id}/samples/{sample_id}", json=update_payload)
        assert update_response.status_code == 404, (
            f"Failed to not update sample with wrong project ID: {update_response.text}"
        )
        assert (
            update_response.json()["detail"]
            == f"Sample with ID {sample_id} does not belong to project with ID {second_project_id}."
        )


def test_delete_text_classification_sample(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to delete a text classification sample.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID from response.
    assert len(file_data_list) == len(text_file_payload)
    file_id_list = []
    for file_data in file_data_list:
        assert file_data["status"] == "Created"
        file_id_list.append(file_data["file_id"])

    # Set sample payload.
    for i, sample_class in enumerate(iterable=sample_class_list):
        sample_payload = {"project_id": project_id, "file_id": file_id_list[i], "class_name": sample_class}

        # Create sample record.
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"

        # Get sample ID from response.
        sample_response_json = sample_response.json()
        sample_id = sample_response_json["_id"]

        # Delete sample record.
        delete_response = client.delete(url=f"/projects/{project_id}/samples/{sample_id}")
        assert delete_response.status_code == 204, f"Failed to delete sample: {delete_response.text}"

        # Attempt to get deleted sample record.
        get_response = client.get(url=f"/projects/{project_id}/samples/{sample_id}")
        assert get_response.status_code == 404, f"Failed to not get deleted sample: {get_response.text}"
        assert get_response.json()["detail"] == f"Sample with ID {sample_id} does not exist."


def test_delete_text_classification_sample_with_wrong_project_id(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to delete a text classification sample with wrong project ID.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create second project to get its ID.
    second_text_project_payload = text_classification_project_payload.copy()
    second_text_project_payload["name"] = "Second Text Classification Project"
    second_project_response = client.post(url="/projects/", json=second_text_project_payload)
    assert second_project_response.status_code == 201, (
        f"Failed to create second project: {second_project_response.text}"
    )
    second_project = second_project_response.json()
    second_project_id = second_project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID from response.
    assert len(file_data_list) == len(text_file_payload)
    file_id_list = []
    for file_data in file_data_list:
        assert file_data["status"] == "Created"
        file_id_list.append(file_data["file_id"])

    # Set sample payload.
    for i, sample_class in enumerate(iterable=sample_class_list):
        sample_payload = {"project_id": project_id, "file_id": file_id_list[i], "class_name": sample_class}

        # Create sample record.
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"
        created_sample_data = sample_response.json()
        created_sample_id = created_sample_data["_id"]

        # Delete the created sample with wrong project ID.
        delete_response = client.delete(url=f"/projects/{second_project_id}/samples/{created_sample_id}")
        assert delete_response.status_code == 404, (
            f"Failed to not delete sample with wrong project ID: {delete_response.text}"
        )
        assert (
            delete_response.json()["detail"]
            == f"Sample with ID {created_sample_id} does not belong to project with ID {second_project_id}."
        )


def test_delete_file_with_text_classification_sample(
    client: TestClient,
    text_classification_project_payload: dict,
    list_text_classification_sample_payload: tuple[list[tuple[str, tuple[str, bytes, str]]], list[str]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to delete a file with an associated text classification sample.
    """
    # Unpack payload.
    text_file_payload, sample_class_list = list_text_classification_sample_payload

    # Create project first.
    project_response = client.post(url="/projects/", json=text_classification_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=text_file_payload)
    assert worker_response.status_code == 202, f"Failed to create file: {worker_response.text}"

    # Wait for the file processing to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID from response.
    assert len(file_data_list) == len(text_file_payload)
    file_id_list = []
    for file_data in file_data_list:
        assert file_data["status"] == "Created"
        file_id_list.append(file_data["file_id"])

    # Set sample payload.
    for i, sample_class in enumerate(iterable=sample_class_list):
        sample_payload = {"project_id": project_id, "file_id": file_id_list[i], "class_name": sample_class}

        # Create sample record.
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=sample_payload)
        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"

    # Get all samples of the current project.
    get_samples_response = client.get(url=f"/projects/{project_id}/samples/")
    assert get_samples_response.status_code == 200, f"Failed to get samples: {get_samples_response.text}"
    sample_list = get_samples_response.json()
    assert len(sample_list) == len(sample_class_list)

    # Delete file records.
    for i, file_id in enumerate(iterable=file_id_list):
        delete_file_response = client.delete(url=f"/projects/{project_id}/files/{file_id}")
        assert delete_file_response.status_code == 204, f"Failed to delete file: {delete_file_response.text}"

        # Get all samples of the current project after file deletion.
        get_samples_response = client.get(url=f"/projects/{project_id}/samples/")
        assert get_samples_response.status_code == 200, (
            f"Failed to get samples after file deletion: {get_samples_response.text}"
        )
        sample_list_after_deletion = get_samples_response.json()
        assert len(sample_list_after_deletion) == len(sample_class_list) - (i + 1)
