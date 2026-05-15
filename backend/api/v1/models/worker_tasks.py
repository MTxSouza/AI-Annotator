"""
Module with all models related to all worker tasks.
"""

from typing import Any

from pydantic import BaseModel, Field


# Schemas.
class WorkerTaskResult(BaseModel):
    """
    Model to represent the result of a worker task.
    """

    # Fields.
    task_id: str | None = Field(default=None, description="The ID of the worker task.")
    message: str = Field(..., description="The message associated with the worker task result.")


class WorkerTaskStatus(BaseModel):
    """
    Model to represent the status of a worker task.
    """

    # Fields.
    status: str = Field(..., description="The status of the worker task.")
    results: Any | None = Field(default=None, description="The results of the worker task, if available.")
