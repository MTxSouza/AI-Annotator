"""
Module with all endpoints related to worker tasks.
"""

from celery.result import AsyncResult
from celery.states import FAILURE, PENDING, STARTED, SUCCESS
from fastapi import APIRouter, status
from fastapi.params import Path

from backend.api.v1.models.worker_tasks import WorkerTaskStatus
from backend.worker import app as celery_app

# Instantiate the router.
router = APIRouter(
    prefix="/workers/tasks",
    tags=["Workers Tasks"],
)


# Endpoints.
@router.get(path="/{task_id}", response_model=WorkerTaskStatus, status_code=status.HTTP_200_OK)
async def get_worker_task_status_endpoint(
    task_id: str = Path(..., description="The ID of the worker task to retrieve status for"),  # type: ignore
) -> WorkerTaskStatus:
    """
    Endpoint to get the status of a worker task by its ID.

    Returns:
            WorkerTaskStatus: The status of the worker task.
    """
    # Search for the task in the Celery backend.
    task_result = AsyncResult(id=task_id, app=celery_app)

    # Check task state.
    results = None
    if task_result.state == SUCCESS:
        results = task_result.result
    elif task_result.state in [PENDING, STARTED]:
        results = "Task is still in progress."
    elif task_result.state == FAILURE:
        results = f"Task failed with error: {task_result.info}"

    return WorkerTaskStatus(status=task_result.state, results=results)
