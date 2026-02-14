"""
Module with all utilities related to task configuration operations.
"""

from backend.api.v1.models.task_configs import (
    ImageCaptionTaskConfig,
    ImageClassificationTaskConfig,
    ObjectCaptionTaskConfig,
    ObjectDetectionTaskConfig,
    TextClassificationTaskConfig,
    TextTaggingTaskConfig,
)
from backend.database.enums import PyObjectId, Task


# Functions.
def setup_task_config(project_id: str, task: Task) -> dict:
    """
    Utility function to setup the task configuration based on the task type.

    Args:
            project_id (str): The project ID.
            task (Task): The task type.

    Returns:
            dict: The task configuration template.
    """
    # Fix task enum if needed.
    if isinstance(task, Task):
        task_str = task.value
    else:
        task_str = task

    # Get the task configuration class based on the task type.
    task_config_class = get_task_config_model_schema(task=task_str)

    if not task_config_class:
        raise ValueError(f"Unsupported task type: {task_str}")

    # Create task configuration instance.
    task_config_instance = task_config_class(project_id=project_id)
    task_config_instance_dict = task_config_instance.model_dump()
    task_config_instance_dict["project_id"] = PyObjectId(oid=project_id)  # Ensure project_id is PyObjectId.

    return task_config_instance_dict


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
        # Image Tasks.
        Task.OBJECT_DETECTION.value: ObjectDetectionTaskConfig,
        Task.IMAGE_CLASSIFICATION.value: ImageClassificationTaskConfig,
        Task.IMAGE_CAPTION.value: ImageCaptionTaskConfig,
        Task.OBJECT_CAPTION.value: ObjectCaptionTaskConfig,
        # Text Tasks.
        Task.TEXT_CLASSIFICATION.value: TextClassificationTaskConfig,
        Task.TEXT_TAGGING.value: TextTaggingTaskConfig,
    }
    return task_config_model_map.get(task)
