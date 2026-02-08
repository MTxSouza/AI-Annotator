"""
Module with all utilities related to task configuration operations.
"""

from backend.api.v1.models.task_configs import (
    ObjectDetectionTaskConfig,
    SemanticSegmentationTaskConfig,
    TextClassificationTaskConfig,
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
    # Task configuration mapping.
    task_config_mapping = {
        # Images.
        Task.OBJECT_DETECTION.value: ObjectDetectionTaskConfig,
        Task.SEMANTIC_SEGMENTATION.value: SemanticSegmentationTaskConfig,
        # Texts.
        Task.TEXT_CLASSIFICATION.value: TextClassificationTaskConfig,
    }

    # Fix task enum if needed.
    if isinstance(task, Task):
        task_str = task.value
    else:
        task_str = task

    # Get the task configuration class based on the task type.
    task_config_class = task_config_mapping.get(task_str)

    if not task_config_class:
        raise ValueError(f"Unsupported task type: {task_str}")

    # Create task configuration instance.
    task_config_instance = task_config_class(project_id=project_id)
    task_config_instance_dict = task_config_instance.model_dump()
    task_config_instance_dict["project_id"] = PyObjectId(oid=project_id)  # Ensure project_id is PyObjectId.

    return task_config_instance_dict
