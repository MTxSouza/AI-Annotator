"""
Module with all utilities related to task configuration operations.
"""

from backend.database.enums import PyObjectId, Task
from backend.database.utils import get_task_config_model_schema


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
