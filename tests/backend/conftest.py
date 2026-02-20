"""
Main module that setup main configurations for backend tests.
"""

import io
import shutil
import time
from collections.abc import Callable
from contextlib import asynccontextmanager

import numpy as np
import pytest
import soundfile as sf
from celery.states import FAILURE, SUCCESS
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from pymongo import MongoClient

from backend.app import app
from backend.configs import BackendSettings
from backend.database.configs import DatabaseConfig
from backend.worker import app as celery_app


# Session-wide fixtures.
@pytest.fixture(scope="session")
def app_instance():
    """
    Fixture to provide the FastAPI app instance.
    """

    # Test lifespan context.
    @asynccontextmanager
    async def test_lifespan(app: FastAPI):

        # Initialize the database client.
        await DatabaseConfig.initialize_client(
            uri=BackendSettings.database_uri,
            database_name=BackendSettings.database_name,
            port=BackendSettings.database_port,
        )
        await DatabaseConfig._drop_database()  # Clean database before tests.
        yield

        # Close the database client.
        await DatabaseConfig.close_client()

    app.router.lifespan_context = test_lifespan
    app.state.limiter.enabled = False  # Disable rate limiter for tests.
    return app


@pytest.fixture(scope="session", autouse=True)
def client(app_instance: FastAPI):
    """
    Fixture to provide the API client for tests.
    """
    # Provide the API client for tests.
    with TestClient(app=app_instance) as client:
        # Health check before running tests.
        response = client.get(url="/health")
        assert response.status_code == 200
        health_check_response = response.json()
        assert health_check_response.get("ok") == 1.0

        yield client


@pytest.fixture(autouse=True, scope="session")
def setup_celery_worker():
    """
    Fixture to setup the Celery worker for tests.
    """
    # Enable eager mode for Celery to execute tasks synchronously during tests.
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_store_eager_result = True

    yield

    # Reset Celery configuration after tests.
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_store_eager_result = False


@pytest.fixture(autouse=True)
def clear_database():
    """
    Fixture to clear the database before each test.
    """
    # Clear the database before each test.
    client: MongoClient = MongoClient(host=BackendSettings.database_uri, port=BackendSettings.database_port)
    client.drop_database(BackendSettings.database_name)
    yield


# Global fixtures to be used during all tests.
@pytest.fixture
def object_detection_project_payload() -> dict:
    """
    Fixture to provide a sample project payload for object detection.
    """
    return {"name": "Test Project", "task": "Object Detection"}


@pytest.fixture
def text_classification_project_payload() -> dict:
    """
    Fixture to provide a sample project payload for text classification.
    """
    return {"name": "Test Project", "task": "Text Classification"}


@pytest.fixture
def audio_transcription_project_payload() -> dict:
    """
    Fixture to provide a sample project payload for audio transcription.
    """
    return {"name": "Test Project", "task": "Audio Transcription"}


@pytest.fixture
def reset_file_directory():
    """
    Fixture to reset the file storage directory before each module.
    """
    # Reset the static file directory.
    shutil.rmtree(BackendSettings.static_file_directory, ignore_errors=True)


@pytest.fixture
def list_png_image_file_payload() -> Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]]:
    """
    Fixture to provide a list of image file payloads.
    """

    def _wrapper() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
        # Create images.
        IMAGE_SIZE_LIST = [
            (200, 200),
            (300, 150),
            (400, 400),
            (500, 250),
            (600, 300),
            (1280, 720),
            (1920, 1080),
            (3840, 2160),
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
                ("file_list", (f"test_image_{image_size[0]}x{image_size[1]}.png", buffer, "image/png"))
            )

        return image_file_list

    return _wrapper


@pytest.fixture
def list_text_file_payload() -> Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]]:
    """
    Fixture to provide a list of text file payloads.
    """

    def _wrapper() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
        # Create text files.
        text_file_list = []
        for i in range(5):
            # Create text content.
            text_content = f"This is test file number {i + 1}."

            # Store text in bytes buffer.
            buffer = io.BytesIO(initial_bytes=text_content.encode("utf-8"))
            buffer.seek(0)

            # Append to list.
            text_file_list.append(("file_list", (f"test_file_{i + 1}.txt", buffer, "text/plain")))

        return text_file_list

    return _wrapper


@pytest.fixture
def list_wav_audio_file_payload() -> Callable[[], list[tuple[str, tuple[str, io.BytesIO, str]]]]:
    """
    Fixture to create a list of audio file payloads.
    """

    def _wrapper() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
        # Create a simple sine wave audio signal as bytes.
        sample_rate = 16000  # 16 kHz
        audio_file_list = []
        for i in range(5):
            duration = np.random.uniform(1, 5)  # Random duration between 1 and 5 seconds

            signal = np.random.uniform(-1, 1, int(sample_rate * duration)).astype(np.float32)

            # Write the signal to a bytes buffer in WAV format.
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, signal, sample_rate, format="WAV", subtype="PCM_16")
            audio_buffer.seek(0)
            audio_file_list.append(("file_list", (f"test_audio_{i}.wav", audio_buffer, "audio/wav")))

        return audio_file_list

    return _wrapper


# Utility
def check_for_worker_task_completion(client: TestClient, worker_task_id: str, attempts: int = 10) -> list[dict]:  # type: ignore
    """
    Utility function to check for worker task completion.
    """
    for _ in range(attempts):
        response = client.get(url=f"/workers/tasks/{worker_task_id}")
        assert response.status_code == 200, f"Failed to get worker task status: {response.text}"
        task_response = response.json()
        if task_response.get("status") == SUCCESS:
            return task_response.get("results", [])
        elif task_response.get("status") == FAILURE:
            pytest.fail(f"Worker task failed: {task_response.get('results', 'Unknown error')}")
        time.sleep(1)  # Wait before retrying.
    pytest.fail("Worker task did not complete within the expected time frame.")
