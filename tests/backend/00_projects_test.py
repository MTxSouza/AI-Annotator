"""
Module used to test project-related endpoints.
"""
import pytest
from fastapi.testclient import TestClient


# Mocks.
@pytest.fixture
def project_payload() -> dict:
    """
    Fixture to provide a sample project payload.
    """
    return {
        "name": "Test Project",
        "task_type": "Object Detection"
    }

# Tests.
def test_create_project(client: TestClient, project_payload: dict):
    """
    Test the create project endpoint.
    """
    # Send a POST request to create the project.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code.
    assert response.status_code == 201

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task_type"] == project_payload["task_type"]
    assert response_data["description"] is None
    assert response_data["is_private"] is False

def test_create_project_with_password(client: TestClient, project_payload: dict):
    """
    Test the create project endpoint with a password.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Send a POST request to create the project.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code.
    assert response.status_code == 201

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task_type"] == project_payload["task_type"]
    assert response_data["description"] is None
    assert response_data["is_private"] is True
