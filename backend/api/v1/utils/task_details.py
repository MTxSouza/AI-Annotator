"""
Module with all utilities related to task configuration operations.
"""

from backend.api.v1.models.task_details import (
    ImageCaptionTaskDetail,
    ImageClassificationTaskDetail,
    ObjectCaptionTaskDetail,
    ObjectDetectionTaskDetail,
    TextClassificationTaskDetail,
    TextTaggingTaskDetail,
)
from backend.database.enums import Task


# Functions.
def setup_task_detail(task: Task) -> dict:
    """
    Utility function to setup the task configuration based on the task type.

    Args:
            task (Task): The task type.

    Returns:
            dict: The task configuration template.
    """
    # Fix task enum if needed.
    if isinstance(task, Task):
        task_str = task.value
    else:
        task_str = task

    # Get the task detail class based on the task type.
    task_detail_class = get_task_detail_model_schema(task=task_str)

    if not task_detail_class:
        raise ValueError(f"Unsupported task type: {task_str}")

    # Create task detail instance.
    task_detail_instance = task_detail_class()
    task_detail_instance_dict = task_detail_instance.model_dump()

    return task_detail_instance_dict


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


def get_task_detail_model_schema(task: str) -> type | None:
    """
    Get the associated task detail model schema for a given task.

    Args:
            task (str): The task to get the detail model schema for.

    Returns:
            type | None: The associated task detail model schema for the task, or None if not found.
    """
    task_detail_model_map = {
        # Image Tasks.
        Task.OBJECT_DETECTION.value: ObjectDetectionTaskDetail,
        Task.IMAGE_CLASSIFICATION.value: ImageClassificationTaskDetail,
        Task.IMAGE_CAPTION.value: ImageCaptionTaskDetail,
        Task.OBJECT_CAPTION.value: ObjectCaptionTaskDetail,
        # Text Tasks.
        Task.TEXT_CLASSIFICATION.value: TextClassificationTaskDetail,
        Task.TEXT_TAGGING.value: TextTaggingTaskDetail,
    }
    return task_detail_model_map.get(task)
