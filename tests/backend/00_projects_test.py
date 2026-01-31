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
        "task": "Object Detection"
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
    assert response_data["task"] == project_payload["task"]
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
    assert response_data["task"] == project_payload["task"]
    assert response_data["description"] is None
    assert response_data["is_private"] is True

def test_create_project_duplicate_name(client: TestClient, project_payload: dict):
    """
    Test the create project endpoint with a duplicate project name.
    """
    # Create the first project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201

    # Attempt to create a second project with the same name.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code for conflict.
    assert response.status_code == 409

def test_get_non_private_project(client: TestClient, project_payload: dict):
    """
    Test retrieving a non-private project.
    """
    # Create a non-private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Retrieve the project.
    response = client.get(url="/projects/%s" % project_id)

    # Assert the response status code.
    assert response.status_code == 200

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]

def test_get_private_project(client: TestClient, project_payload: dict):
    """
    Test retrieving a private project.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create a private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Retrieve the project.
    response = client.get(url="/projects/%s" % project_id)

    # Assert the response status code.
    assert response.status_code == 401

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(url="/auth/token", data={"username": project_id, "password": project_payload["password"]})

    # Assert the authentication response status code.
    assert auth_response.status_code == 200
    access_token = auth_response.json()["access_token"]

    # Retrieve the project with the access token.
    response = client.get(url="/projects/%s" % project_id, headers={"Authorization": f"Bearer {access_token}"})

    # Assert the response status code.
    assert response.status_code == 200

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]
