"""
Main module that setup main configurations for backend tests.
"""
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

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
            port=BackendSettings.database_port
        )
        await DatabaseConfig._drop_database()  # Clean database before tests.
        yield

        # Close the database client.
        await DatabaseConfig.close_client()

    app.router.lifespan_context = test_lifespan
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
