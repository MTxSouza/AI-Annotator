"""
Module used to test audio file-related endpoints.
"""

import io

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient


# Mocks.
@pytest.fixture
def corrupt_audio_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a corrupt audio file payload.
    """
    # Create corrupt audio content.
    sample_rate = 16000  # 16 kHz
    duration = 2  # 2 seconds

    signal = np.random.uniform(-1, 1, int(sample_rate * duration)).astype(np.float32)

    # Write the signal to a bytes buffer in WAV format.
    audio_buffer = io.BytesIO()
    sf.write(audio_buffer, signal, sample_rate, format="WAV", subtype="PCM_16")

    # Truncate the buffer to make it corrupt.
    audio_bytes = audio_buffer.getvalue()
    corrupt_audio_bytes = audio_bytes[: len(audio_bytes) // 2]  # Keep only the first half
    corrupt_audio_buffer = io.BytesIO(initial_bytes=corrupt_audio_bytes)
    corrupt_audio_buffer.seek(0)

    return [("file_list", ("corrupt_audio.wav", corrupt_audio_buffer, "audio/wav"))]


# Tests.
def test_create_audio_file_record(
    client: TestClient,
    audio_transcription_project_payload: dict,
    list_wav_audio_file_payload: list[tuple[str, tuple[str, bytes, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an audio file record.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Check number of files and samples in project response.
    project_details = project.get("details", {})
    assert project_details["number_of_files"] == 0
    assert project_details["number_of_samples"] == 0
    assert project["details"]["total_duration_in_seconds"] == 0.0

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=list_wav_audio_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(list_wav_audio_file_payload)

    file_id_list = []
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Created"
        assert file_data["message"] == f"Audio file '{list_wav_audio_file_payload[i][1][0]}' uploaded successfully."
        file_id_list.append(file_data["file_id"])

    # Get project again to check number of files and samples.
    project_response = client.get(url=f"/projects/{project_id}")
    assert project_response.status_code == 200, f"Failed to get project: {project_response.text}"
    project = project_response.json()
    assert project["details"]["number_of_files"] == len(list_wav_audio_file_payload)
    assert project["details"]["number_of_samples"] == 0
    assert project["details"]["total_duration_in_seconds"] > 0.0


def test_create_duplicate_audio_file_record(
    client: TestClient,
    audio_transcription_project_payload: dict,
    list_wav_audio_file_payload: list[tuple[str, tuple[str, bytes, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to check that creating a duplicate audio file record is handled properly.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=list_wav_audio_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Attempt to create duplicate file record.
    duplicate_file_response = client.post(url=f"/projects/{project_id}/files/", files=list_wav_audio_file_payload)
    assert duplicate_file_response.status_code == 201, (
        f"Failed to create duplicate file: {duplicate_file_response.text}"
    )

    # Check response.
    duplicate_file_response_json = duplicate_file_response.json()
    assert "data" in duplicate_file_response_json
    assert len(duplicate_file_response_json["data"]) == len(list_wav_audio_file_payload)
    for i, file_data in enumerate(iterable=duplicate_file_response_json["data"]):
        assert file_data["status"] == "Skipped"
        assert file_data["message"] == f"File '{list_wav_audio_file_payload[i][1][0]}' already exists."


def test_create_corrupt_audio_file_record(
    client: TestClient,
    audio_transcription_project_payload: dict,
    corrupt_audio_file_payload: list[tuple[str, tuple[str, bytes, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to check that creating a corrupt audio file record is handled properly.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project = project_response.json()
    project_id = project["_id"]

    # Attempt to create file record with corrupt audio file.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=corrupt_audio_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(corrupt_audio_file_payload)
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == f"Corrupted file: {corrupt_audio_file_payload[i][1][0]}."


def test_create_image_file_format_record(
    client: TestClient,
    audio_transcription_project_payload: dict,
    list_png_image_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create an image file record in an audio transcription project.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=list_png_image_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(list_png_image_file_payload)
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Invalid file format for this project: png."


def test_create_text_file_format_record(
    client: TestClient,
    audio_transcription_project_payload: dict,
    list_text_file_payload: list[tuple[str, tuple[str, io.BytesIO, str]]],
    reset_file_directory: None,  # Used to reset file directory
):
    """
    Test to create a text file record in an audio transcription project.
    """
    # Create project first.
    project_response = client.post(url="/projects/", json=audio_transcription_project_payload)
    assert project_response.status_code == 201, f"Failed to create project: {project_response.text}"
    project_id = project_response.json()["_id"]

    # Create file record.
    file_response = client.post(url=f"/projects/{project_id}/files/", files=list_text_file_payload)
    assert file_response.status_code == 201, f"Failed to create file: {file_response.text}"

    # Check response.
    file_response_json = file_response.json()
    assert "data" in file_response_json
    assert len(file_response_json["data"]) == len(list_text_file_payload)
    for i, file_data in enumerate(iterable=file_response_json["data"]):
        assert file_data["status"] == "Failed"
        assert file_data["message"] == "Invalid file format for this project: txt."
