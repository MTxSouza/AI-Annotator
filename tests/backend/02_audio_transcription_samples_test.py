"""
Module used to test audio transcription sample-related endpoints.
"""

import io
from collections.abc import Callable

import bson
import pytest
from fastapi.testclient import TestClient

from tests.backend.conftest import check_for_worker_task_completion


# Mocks.
@pytest.fixture
def audio_transcription_sample_payload(
    list_wav_audio_file_payload: Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]],
) -> tuple[list[tuple[str, tuple[str, io.BytesIO, str]]], list[dict]]:
    """
    Fixture to provide an audio transcription sample payload.
    """
    # Create audio file payload.
    list_wav_audio_file = list_wav_audio_file_payload()

    # Define transcriptions.
    audio_transcription_list = []
    for i in range(len(list_wav_audio_file)):
        audio_transcription_list.append({"text": f"Transcription for audio file {i}"})

    return list_wav_audio_file, audio_transcription_list


# Tests.
def test_create_audio_transcription_sample(
    client: TestClient,
    audio_transcription_project_payload: dict,
    audio_transcription_sample_payload: tuple[list[tuple[str, tuple[str, io.BytesIO, str]]], list[dict]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an audio transcription sample.
    """
    # Unpack sample payload.
    list_wav_audio_file, audio_transcription_list = audio_transcription_sample_payload

    # Create a project.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=list_wav_audio_file)
    assert worker_response.status_code == 202, f"Failed to create file record: {worker_response.text}"

    # Wait for worker task to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == len(list_wav_audio_file)

    # Get file ID from response.
    file_id_list = []
    for file_data in file_data_list:
        assert file_data["status"] == "Created"
        file_id = file_data["file_id"]
        file_id_list.append(file_id)
    assert len(file_id_list) > 0, "File IDs not found in response"

    # Set sample payload.
    for i in range(len(audio_transcription_list)):
        current_audio_transcription_sample_payload = audio_transcription_list[i]
        current_audio_transcription_sample_payload["project_id"] = project_id
        current_audio_transcription_sample_payload["file_id"] = file_id_list[i]

        # Create sample record.
        sample_response = client.post(
            url=f"/projects/{project_id}/samples/", json=current_audio_transcription_sample_payload
        )
        assert sample_response.status_code == 201, f"Failed to create sample record: {sample_response.text}"

        # Check response.
        sample = sample_response.json()
        assert sample["text"] == current_audio_transcription_sample_payload["text"]

    # Get project details again and check number of files and samples.
    project_response = client.get(url=f"/projects/{project_id}/")
    assert project_response.status_code == 200, f"Failed to get project details: {project_response.text}"
    project_details = project_response.json().get("details", {})
    assert project_details["number_of_files"] == len(list_wav_audio_file)
    assert project_details["number_of_samples"] == len(audio_transcription_list)


def test_create_more_than_one_audio_transcription_sample_per_file(
    client: TestClient,
    audio_transcription_project_payload: dict,
    audio_transcription_sample_payload: tuple[list[tuple[str, tuple[str, io.BytesIO, str]]], list[dict]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create more than one audio transcription sample per file.
    """
    # Unpack sample payload.
    list_wav_audio_file, audio_transcription_list = audio_transcription_sample_payload

    # Create a project.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0

    # Create file record.
    single_wav_audio_file = [list_wav_audio_file[0]]
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=single_wav_audio_file)
    assert worker_response.status_code == 202, f"Failed to create file record: {worker_response.text}"

    # Wait for worker task to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Check response.
    assert len(file_data_list) == 1
    file_id = file_data_list[0]["file_id"]

    # Set sample payload.
    single_audio_transcription = audio_transcription_list[0]
    single_audio_transcription["project_id"] = project_id
    single_audio_transcription["file_id"] = file_id
    sample_response = client.post(url=f"/projects/{project_id}/samples/", json=single_audio_transcription)
    assert sample_response.status_code == 201, f"Failed to create sample record: {sample_response.text}"

    # Set second sample payload with same file ID.
    second_audio_transcription = audio_transcription_list[1]
    second_audio_transcription["project_id"] = project_id
    second_audio_transcription["file_id"] = file_id
    second_sample_response = client.post(url=f"/projects/{project_id}/samples/", json=second_audio_transcription)
    assert second_sample_response.status_code == 400, (
        f"Failed to not create second sample with same file ID: {second_sample_response.text}"
    )
    assert (
        second_sample_response.json().get("detail")
        == f"Number of samples for file with ID {file_id} for the task Audio Transcription cannot exceed 1."
    )


def test_create_audio_transcription_sample_with_nonexistent_file(
    client: TestClient,
    audio_transcription_project_payload: dict,
    audio_transcription_sample_payload: tuple[list[tuple[str, tuple[str, io.BytesIO, str]]], list[dict]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an audio transcription sample with a nonexistent file ID.
    """
    # Unpack sample payload.
    _, audio_transcription_list = audio_transcription_sample_payload

    # Create a project.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Set sample payload with nonexistent file ID.
    single_audio_transcription = audio_transcription_list[0]
    single_audio_transcription["project_id"] = project_id
    single_audio_transcription["file_id"] = str(bson.ObjectId())  # Generate random ObjectId for file ID

    # Create sample record.
    sample_response = client.post(url=f"/projects/{project_id}/samples/", json=single_audio_transcription)
    assert sample_response.status_code == 404, (
        f"Failed to not create sample with nonexistent file ID: {sample_response.text}"
    )
    assert sample_response.json()["detail"] == f"File with ID {single_audio_transcription['file_id']} does not exist."


def test_update_audio_transcription_sample(
    client: TestClient,
    audio_transcription_project_payload: dict,
    audio_transcription_sample_payload: tuple[list[tuple[str, tuple[str, io.BytesIO, str]]], list[dict]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to update an audio transcription sample.
    """
    # Unpack sample payload.
    list_wav_audio_file, audio_transcription_list = audio_transcription_sample_payload

    # Create a project.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    worker_response = client.post(url=f"/projects/{project_id}/files/", files=list_wav_audio_file)
    assert worker_response.status_code == 202, f"Failed to create file record: {worker_response.text}"

    # Wait for worker task to complete.
    worker_response_json = worker_response.json()
    assert "task_id" in worker_response_json, "Response does not contain task_id"
    worker_task_id = worker_response_json["task_id"]
    file_data_list = check_for_worker_task_completion(client=client, worker_task_id=worker_task_id)

    # Get file ID from response.
    file_id_list = []
    for file_data in file_data_list:
        assert file_data["status"] == "Created"
        file_id = file_data["file_id"]
        file_id_list.append(file_id)
    assert len(file_id_list) > 0, "File IDs not found in response"

    # Create sample records.
    sample_id_list = []
    for i in range(len(audio_transcription_list)):
        current_audio_transcription_sample = audio_transcription_list[i]
        current_audio_transcription_sample["project_id"] = project_id
        current_audio_transcription_sample["file_id"] = file_id_list[i]
        sample_response = client.post(url=f"/projects/{project_id}/samples/", json=current_audio_transcription_sample)

        assert sample_response.status_code == 201, f"Failed to create sample: {sample_response.text}"
        sample_id_list.append(sample_response.json()["_id"])

    # Update sample records.
    for i in range(len(sample_id_list)):
        sample_id = sample_id_list[i]
        updated_text = f"Updated transcription for audio file {i}"
        update_payload = {"text": updated_text}
        update_response = client.put(url=f"/projects/{project_id}/samples/{sample_id}/", json=update_payload)
        assert update_response.status_code == 201, f"Failed to update sample: {update_response.text}"

        # Check response.
        sample_response_json = update_response.json()
        assert sample_response_json["_id"] == sample_id
        assert sample_response_json["project_id"] == project_id
        assert sample_response_json["file_id"] == file_id_list[i]
        assert sample_response_json["text"] == updated_text
