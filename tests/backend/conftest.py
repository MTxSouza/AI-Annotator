"""
Main module that setup main configurations for backend tests.
"""

import random
import string
import time
from contextlib import asynccontextmanager

import pytest
from celery.states import FAILURE, SUCCESS
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

from backend.app import app
from backend.configs import BackendSettings
from backend.database.configs import DatabaseConfig
from backend.worker import app as celery_app
from tests.files import AudioFileTest, ImageFileTest, TextFileTest


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
    client.close()


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
def text_100words_payload() -> bytes:
    """
    Utility function to create a sample text file payload with 100 words.
    """
    # Create text content.
    text = random.choices(string.ascii_letters + string.digits + string.punctuation + " ", k=100)
    content = TextFileTest.write_content(content="".join(text))
    return content


@pytest.fixture
def text_1000words_payload() -> bytes:
    """
    Utility function to create a sample text file payload with 1000 words.
    """
    # Create text content.
    text = random.choices(string.ascii_letters + string.digits + string.punctuation + " ", k=1000)
    content = TextFileTest.write_content(content="".join(text))
    return content


@pytest.fixture
def text_10000words_payload() -> bytes:
    """
    Utility function to create a sample text file payload with 10000 words.
    """
    # Create text content.
    text = random.choices(string.ascii_letters + string.digits + string.punctuation + " ", k=10000)
    content = TextFileTest.write_content(content="".join(text))
    return content


@pytest.fixture
def image_200x200_payload() -> bytes:
    """
    Utility function to create a sample image file payload.
    """
    # Create image content.
    content = ImageFileTest.write_content(width=200, height=200, channels=3)
    return content


@pytest.fixture
def image_300x300_payload() -> bytes:
    """
    Utility function to create a sample image file payload.
    """
    # Create image content.
    content = ImageFileTest.write_content(width=300, height=300, channels=3)
    return content


@pytest.fixture
def image_400x400_payload() -> bytes:
    """
    Utility function to create a sample image file payload.
    """
    # Create image content.
    content = ImageFileTest.write_content(width=400, height=400, channels=3)
    return content


@pytest.fixture
def audio_5s_payload() -> bytes:
    """
    Utility function to create a sample audio file payload with 5 seconds of audio.
    """
    return AudioFileTest.write_content(duration=5, sample_rate=44100)


@pytest.fixture
def audio_10s_payload() -> bytes:
    """
    Utility function to create a sample audio file payload with 10 seconds of audio.
    """
    return AudioFileTest.write_content(duration=10, sample_rate=44100)


@pytest.fixture
def audio_20s_payload() -> bytes:
    """
    Utility function to create a sample audio file payload with 20 seconds of audio.
    """
    return AudioFileTest.write_content(duration=20, sample_rate=44100)


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
