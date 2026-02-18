"""
Module with all models related to all worker tasks.
"""

from pydantic import BaseModel, Field


# Schemas.
class WorkerTaskResult(BaseModel):
    """
    Model to represent the result of a worker task.
    """

    # Fields.
    task_id: str = Field(..., description="The ID of the worker task.")
    message: str = Field(..., description="The message associated with the worker task result.")
