"""
Module used to test project-related endpoints.
"""

import time

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
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]
    assert response_data["description"] is None
    assert response_data["is_private"] is False
    assert "password" not in response_data
    assert "hashed_password" not in response_data
    assert "details" in response_data


def test_create_project_with_password(client: TestClient, project_payload: dict):
    """
    Test the create project endpoint with a password.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Send a POST request to create the project.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code.
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]
    assert response_data["description"] is None
    assert response_data["is_private"] is True


def test_logout_project(client: TestClient, project_payload: dict):
    """
    Test the logout project endpoint.
    """
    # Send a POST request to create the project.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code.
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    # Logout of the project.
    project_id = response.json()["_id"]
    response = client.post(url="/auth/logout")

    # Assert the logout response status code.
    assert response.status_code == 204, f"Failed to logout of project: {response.text}"

    # Attempt to retrieve the project after logout.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to get expected not found response after logout: {response.text}"


def test_logout_from_private_project(client: TestClient, project_payload: dict):
    """
    Test the logout from a private project endpoint.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Send a POST request to create the project.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code.
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    # Logout of the project.
    project_id = response.json()["_id"]
    response = client.post(url="/auth/logout")

    # Assert the logout response status code.
    assert response.status_code == 204, f"Failed to logout of project: {response.text}"

    # Attempt to retrieve the project after logout.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 401, f"Failed to get expected unauthorized response after logout: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"


def test_create_project_duplicate_name(client: TestClient, project_payload: dict):
    """
    Test the create project endpoint with a duplicate project name.
    """
    # Create the first project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    # Attempt to create a second project with the same name.
    response = client.post(url="/projects/", json=project_payload)

    # Assert the response status code for conflict.
    assert response.status_code == 409, f"Failed to get expected conflict response: {response.text}"


def test_get_non_private_project(client: TestClient, project_payload: dict):
    """
    Test retrieving a non-private project.
    """
    # Create a non-private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Retrieve the project.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to get project: {response.text}"

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
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Retrieve the project.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 401, f"Failed to get expected unauthorized response: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )

    # Assert the authentication response status code.
    assert auth_response.status_code == 201, f"Failed to authenticate: {auth_response.text}"

    # Retrieve the project with the access token.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to get project with access token: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]

    # Logout of the project.
    response = client.post(url="/auth/logout")

    # Assert the logout response status code.
    assert response.status_code == 204, f"Failed to logout of project: {response.text}"


def test_update_project_name(client: TestClient, project_payload: dict):
    """
    Test updating a project's name.
    """
    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    created_project = response.json()
    project_id = created_project["_id"]
    created_at_0 = created_project["created_at"]
    updated_at_0 = created_project["updated_at"]

    # Sleep for a short time to ensure updated_at timestamp will be different after the update.
    time.sleep(2)

    # Update the project's name.
    updated_name = "Updated Project Name"
    update_payload = {"name": updated_name}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    updated_project = response.json()
    created_at_1 = updated_project["created_at"]
    updated_at_1 = updated_project["updated_at"]

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to update project name: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == updated_name
    assert response_data["task"] == project_payload["task"]

    # Assert creation and update timestamps.
    assert created_at_0 == created_at_1, "Creation timestamp should not change on update"
    assert updated_at_0 != updated_at_1, "Update timestamp should change on update"


def test_update_private_project_name(client: TestClient, project_payload: dict):
    """
    Test updating a private project's name.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Update the project's name.
    updated_name = "Updated Project Name"
    update_payload = {"name": updated_name}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 401, f"Failed to get expected unauthorized response: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )

    # Assert the authentication response status code.
    assert auth_response.status_code == 201, f"Failed to authenticate: {auth_response.text}"

    # Update the project's name with the access token.
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to update project name: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == updated_name
    assert not response_data["description"]
    assert response_data["task"] == project_payload["task"]
    assert response_data["is_private"]

    # Logout of the project.
    response = client.post(url="/auth/logout")

    # Assert the logout response status code.
    assert response.status_code == 204, f"Failed to logout of project: {response.text}"


def test_update_project_password(client: TestClient, project_payload: dict):
    """
    Test updating a project's password.
    """
    # Create a project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Get the project to ensure it is non-private.
    response = client.get(url=f"/projects/{project_id}")
    assert response.status_code == 200, f"Failed to get project: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert not response_data["is_private"]

    # Update the project's password.
    new_password = "newsecurepassword"
    update_payload = {"password": new_password}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to update project password: {response.text}"

    # Get the project to ensure it is now private.
    response = client.get(url=f"/projects/{project_id}")
    assert response.status_code == 200, f"Failed to get project after updating password: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["name"] == project_payload["name"]
    assert response_data["task"] == project_payload["task"]
    assert response_data["is_private"]

    # Logout of the project.
    response = client.post(url="/auth/logout")

    # Assert the logout response status code.
    assert response.status_code == 204, f"Failed to logout of project: {response.text}"


def test_update_private_project_to_non_private(client: TestClient, project_payload: dict):
    """
    Test updating a private project to be non-private.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create a private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )
    assert auth_response.status_code == 201, f"Failed to authenticate: {auth_response.text}"

    # Update the project's password to None (make it non-private).
    update_payload = {"password": None}
    response = client.put(url=f"/projects/{project_id}", json=update_payload)

    # Assert the response status code.
    assert response.status_code == 200, f"Failed to update project to non-private: {response.text}"

    # Get the project to ensure it is now non-private.
    response = client.get(url=f"/projects/{project_id}")
    assert response.status_code == 200, f"Failed to get project after updating to non-private: {response.text}"

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
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Delete the project.
    response = client.delete(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 204, f"Failed to delete project: {response.text}"

    # Attempt to retrieve the deleted project.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code for not found.
    assert response.status_code == 404, f"Failed to get expected not found response: {response.text}"

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
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project_id = response.json()["_id"]

    # Attempt to delete the project without authentication.
    response = client.delete(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 401, f"Failed to get expected unauthorized response: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated to access this private project"

    # Authenticate to get access token.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id, "password": project_payload["password"]}
    )
    assert auth_response.status_code == 201, f"Failed to authenticate: {auth_response.text}"

    # Delete the project with the access token.
    response = client.delete(url=f"/projects/{project_id}")

    # Assert the response status code.
    assert response.status_code == 204, f"Failed to delete project: {response.text}"

    # Attempt to retrieve the deleted project.
    response = client.get(url=f"/projects/{project_id}")

    # Assert the response status code for not found.
    assert response.status_code == 404, f"Failed to get expected not found response: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Project not found"


def test_get_private_project_with_token_of_another_project(client: TestClient, project_payload: dict):
    """
    Test retrieving a private project with an access token from another project.
    """
    # Add password to the payload.
    project_payload["password"] = "securepassword"

    # Create the first private project.
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create first project: {response.text}"
    project_id_1 = response.json()["_id"]

    # Create the second private project.
    project_payload["name"] = "Second Test Project"
    response = client.post(url="/projects/", json=project_payload)
    assert response.status_code == 201, f"Failed to create second project: {response.text}"
    project_id_2 = response.json()["_id"]

    # Authenticate to get access token for the first project.
    auth_response = client.post(
        url="/auth/token", data={"username": project_id_1, "password": project_payload["password"]}
    )
    assert auth_response.status_code == 201, f"Failed to authenticate for the first project: {auth_response.text}"

    # Attempt to retrieve the second private project with the first project's access token.
    response = client.get(url=f"/projects/{project_id_2}")

    # Assert the response status code.
    assert response.status_code == 403, f"Failed to get expected forbidden response: {response.text}"

    # Assert the response data.
    response_data = response.json()
    assert response_data["detail"] == "Token subject does not match project ID"

    # Logout of the project.
    response = client.post(url="/auth/logout")

    # Assert the logout response status code.
    assert response.status_code == 204, f"Failed to logout of project: {response.text}"
