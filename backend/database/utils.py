"""
Module with basic functions to be used in database operations.
"""

from datetime import UTC, datetime

from backend.api.v1.models.task_configs import ObjectDetectionTaskConfig, TextClassificationTaskConfig
from backend.database.enums import Task


# Functions.
def get_current_datetime() -> datetime:
    """
    Function to get the current date and time.

    Returns:
            datetime: The current date and time.
    """
    return datetime.now(tz=UTC)


def get_task_file(task: str) -> str | None:
    """
    Get the associated file type for a given task.

    Args:
            task (str): The task to get the file type for.

    Returns:
            str | None: The associated file type for the task, or None if not found.
    """
    task_file_map = {
        Task.OBJECT_DETECTION.value: "image",
        Task.IMAGE_CLASSIFICATION.value: "image",
        Task.IMAGE_CAPTION.value: "image",
        Task.OBJECT_CAPTION.value: "image",
        Task.TEXT_CLASSIFICATION.value: "text",
        Task.TEXT_TAGGING.value: "text",
        Task.AUDIO_CLASSIFICATION.value: "audio",
        Task.AUDIO_CAPTION.value: "audio",
    }
    return task_file_map.get(task)


def get_task_config_model_schema(task: str) -> type | None:
    """
    Get the associated task configuration model schema for a given task.

    Args:
            task (str): The task to get the configuration model schema for.

    Returns:
            type | None: The associated task configuration model schema for the task, or None if not found.
    """
    task_config_model_map = {
        Task.OBJECT_DETECTION.value: ObjectDetectionTaskConfig,
        Task.TEXT_CLASSIFICATION.value: TextClassificationTaskConfig,
    }
    return task_config_model_map.get(task)
