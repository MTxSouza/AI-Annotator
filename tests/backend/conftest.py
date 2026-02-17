"""
Main module that setup main configurations for backend tests.
"""

import io
import shutil
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from pymongo import MongoClient

from backend.app import app
from backend.configs import BackendSettings
from backend.database.configs import DatabaseConfig


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
def image_project_payload() -> dict:
    """
    Fixture to provide a sample project payload for image files.
    """
    return {"name": "Test Project", "task": "Object Detection"}


@pytest.fixture
def text_project_payload() -> dict:
    """
    Fixture to provide a sample project payload for text files.
    """
    return {"name": "Test Project", "task": "Text Classification"}


@pytest.fixture
def reset_file_directory():
    """
    Fixture to reset the file storage directory before each module.
    """
    # Reset the static file directory.
    shutil.rmtree(BackendSettings.static_file_directory, ignore_errors=True)


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
        image_file_list.append(("file_list", (f"test_image_{image_size[0]}x{image_size[1]}.png", buffer, "image/png")))

    return image_file_list


@pytest.fixture
def list_text_file_payload() -> list[tuple[str, tuple[str, io.BytesIO, str]]]:
    """
    Fixture to provide a list of text file payloads.
    """
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
