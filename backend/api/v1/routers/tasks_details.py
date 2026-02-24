"""
Module with all endpoints related to tasks operations.
"""

from fastapi import APIRouter, status

from backend.api.v1.models.task_details import Task
from backend.api.v1.utils.task_details import get_tasks

# Instantiate the router.
router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Endpoints.
@router.get(path="/", name="Get Tasks", response_model=list[Task], status_code=status.HTTP_200_OK)
async def get_tasks_endpoint() -> list[Task]:
    """
    Endpoint to get all tasks.

    Returns:
            list[Task]: List of all tasks.
    """
    return get_tasks()  # type: ignore
