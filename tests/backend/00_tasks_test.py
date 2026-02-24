"""
Module used to test task-related endpoints.
"""

import pytest
from fastapi.testclient import TestClient


# Mocks.
@pytest.fixture
def available_task_list() -> list[str]:
    return ["Object Detection", "Text Classification", "Audio Transcription"]


# Tests.
def test_get_available_tasks(client: TestClient, available_task_list: list[str]):
    """
    Test get all available tasks.
    """
    # Get all available tasks.
    response = client.get(url="/tasks/")

    # Assert response status code.
    assert response.status_code == 200, f"Failed to get tasks: {response.text}"

    # Assert response data.
    task_list = response.json()
    assert len(task_list) == len(available_task_list), (
        f"Expected {len(available_task_list)} tasks, got {len(task_list)}"
    )
    for task in task_list:
        assert task["name"] in available_task_list, f"Unexpected task name: {task['name']}"
        assert task["description"] is not None, "Task description is missing"
        assert task["file_format_list"], "Task file format list is empty"
