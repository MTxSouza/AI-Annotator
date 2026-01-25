"""
Main module that setup main configurations for backend tests.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app import app


# Session-wide fixtures.
@pytest.fixture(scope="session", autouse=True)
def client():
    """
    Fixture to provide the API client for tests.
    """
    # Provide the API client for tests.
    with TestClient(app=app) as client:

        # Health check before running tests.
        response = client.get(url="/health")
        assert response.status_code == 200
        health_check_response = response.json()
        assert health_check_response.get("ok") == 1.0

        yield client
