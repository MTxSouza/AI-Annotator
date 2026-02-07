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
    return {"name": "Test Project", "task": "Object Detection"}


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
    assert "password" not in response_data
    assert "hashed_password" not in response_data
    assert "configs" in response_data
    assert response_data["configs"]["project_id"] == response_data["_id"]


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
    response = client.get(url=f"/projects/{project_id}")

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
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 401

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )

    # Assert the authentication response status code.
    assert auth_response.status_code == 201
    access_token = auth_response.json()["access_token"]

    # Retrieve the project with the access token.
    response = client.get(url=f"/projects/{project_id}", headers={"Authorization": f"Bearer {access_token}"})

    # Assert the response status code.
    assert response.status_code == 200

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]


def test_update_project_name(client: TestClient, project_payload: dict):
    """
    Test updating a project's name.
    """
    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Update the project's name.
    updated_name = "Updated Project Name"
    update_payload = {"name": updated_name}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 201

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == updated_name
    assert response_data["task"] == project_payload["task"]


def test_update_private_project_name(client: TestClient, project_payload: dict):
    """
    Test updating a private project's name.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Update the project's name.
    updated_name = "Updated Project Name"
    update_payload = {"name": updated_name}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 401

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )

    # Assert the authentication response status code.
    assert auth_response.status_code == 201
    access_token = auth_response.json()["access_token"]

    # Update the project's name with the access token.
    response = client.put(
        url=f"/projects/{project_id}", json=update_payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    # Assert the response status code.
    assert response.status_code == 201

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == updated_name
    assert response_data["task"] == project_payload["task"]


def test_update_project_password(client: TestClient, project_payload: dict):
    """
    Test updating a project's password.
    """
    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Get the project to ensure it is non-private.
    response = client.get(url=f"/projects/{project_id}")
    assert response.status_code == 200

    # Assert the response data.
    response_data = response.json()
    assert not response_data["is_private"]

    # Update the project's password.
    new_password = "newsecurepassword"
    update_payload = {"password": new_password}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 201

    # Get the project to ensure it is now private.
    response = client.get(url=f"/projects/{project_id}")
    assert response.status_code == 401

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(url="/auth/token", data={"username": project_id, "password": new_password})
    assert auth_response.status_code == 201
    access_token = auth_response.json()["access_token"]

    # Retrieve the project with the access token.
    response = client.get(url=f"/projects/{project_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]
    assert response_data["is_private"]


def test_update_private_project_to_non_private(client: TestClient, project_payload: dict):
    """
    Test updating a private project to be non-private.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create a private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )
    assert auth_response.status_code == 201
    access_token = auth_response.json()["access_token"]

    # Update the project's password to None (make it non-private).
    update_payload = {"password": None}
    response = client.put(
        url=f"/projects/{project_id}", json=update_payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    # Assert the response status code.
    assert response.status_code == 201

    # Get the project to ensure it is now non-private.
    response = client.get(url=f"/projects/{project_id}")
    assert response.status_code == 200

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]
    assert not response_data["is_private"]


def test_delete_project(client: TestClient, project_payload: dict):
    """
    Test deleting a project.
    """
    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Delete the project.
    response = client.delete(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 204

    # Attempt to retrieve the deleted project.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code for not found.
    assert response.status_code == 404

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Project not found"


def test_delete_private_project(client: TestClient, project_payload: dict):
    """
    Test deleting a private project.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create a private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201
    project_id = response.json()["_id"]

    # Attempt to delete the project without authentication.
    response = client.delete(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 401

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )
    assert auth_response.status_code == 201
    access_token = auth_response.json()["access_token"]

    # Delete the project with the access token.
    response = client.delete(url=f"/projects/{project_id}", headers={"Authorization": f"Bearer {access_token}"})

    # Assert the response status code.
    assert response.status_code == 204

    # Attempt to retrieve the deleted project.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code for not found.
    assert response.status_code == 404

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Project not found"
