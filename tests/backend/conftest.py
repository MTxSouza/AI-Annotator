"""
Main module that setup main configurations for backend tests.
"""

import shutil
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

from backend.api.v1.utils.files import STATIC_FILE_DIRECTORY
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
    shutil.rmtree(STATIC_FILE_DIRECTORY, ignore_errors=True)
