"""
Module with all utilities related to task configuration operations.
"""

from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.task_details import (
    ObjectDetectionTaskDetail,
    TextClassificationTaskDetail,
)
from backend.database.configs import Collections
from backend.database.enums import PyObjectId, Task


# Functions.
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
        Task.AUDIO_TRANSCRIPTION.value: "audio",
    }
    return task_file_map.get(task)


def get_valid_number_of_samples_per_file(task: str) -> int | None:
    """
    Get the valid number of samples per file for a given task. If it returns -1, there is no limit to
    the number of samples/annotations per file.

    Args:
            task (str): The task to get the valid number of samples per file for.

    Returns:
            int | None: The valid number of samples per file for the task, or None if not found.
    """
    task_samples_per_file_map = {
        Task.OBJECT_DETECTION.value: -1,
        Task.IMAGE_CLASSIFICATION.value: 1,
        Task.IMAGE_CAPTION.value: -1,
        Task.OBJECT_CAPTION.value: -1,
        Task.TEXT_CLASSIFICATION.value: 1,
        Task.TEXT_TAGGING.value: -1,
        Task.AUDIO_CLASSIFICATION.value: 1,
        Task.AUDIO_TRANSCRIPTION.value: 1,
    }
    return task_samples_per_file_map.get(task)


async def setup_task_detail(task: Task, project_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Utility function to setup the task configuration based on the task type.

    Args:
            task (Task): The task type.
            project_id (str | PyObjectId): The ID of the project to setup the task detail for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The task configuration template.
    """
    # Fix task enum if needed.
    if isinstance(task, Task):
        task_str = task.value
    else:
        task_str = task

    # Get the task detail class based on the task type.
    task_detail_instance_dict = await setup_task_detail_model_schema(task=task_str, project_id=project_id, db=db)

    if not task_detail_instance_dict:
        raise ValueError(f"Unsupported task type: {task_str}")

    return task_detail_instance_dict


async def setup_task_detail_model_schema(task: str, project_id: str | PyObjectId, db: AsyncDatabase) -> dict | None:
    """
    Get the associated task detail model schema for a given task.

    Args:
            task (str): The task to get the detail model schema for.
            project_id (str | PyObjectId): The ID of the project to setup the task detail for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict | None: The associated task detail model schema for the task, or None if not found.
    """
    # Get the task detail setup function.
    task_detail_model_map = {
        # Image Tasks.
        Task.OBJECT_DETECTION.value: _setup_object_detection_task_detail_model_schema,
        Task.IMAGE_CLASSIFICATION.value: None,
        Task.IMAGE_CAPTION.value: None,
        Task.OBJECT_CAPTION.value: None,
        # Text Tasks.
        Task.TEXT_CLASSIFICATION.value: _setup_text_classification_task_detail_model_schema,
        Task.TEXT_TAGGING.value: None,
    }
    task_detail_setup_function = task_detail_model_map.get(task)
    if not task_detail_setup_function:
        return None

    # Setup model schema with setup function.
    task_detail_model_schema = await task_detail_setup_function(project_id, db)
    task_detail_model_schema_dict = task_detail_model_schema.model_dump()

    return task_detail_model_schema_dict


async def _get_number_of_files_and_samples(project_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Get the number of files and samples for a given project.

    Args:
            project_id (str | PyObjectId): The ID of the project to get the number of files and samples for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: A dictionary containing the number of files and samples for the project.
    """
    # Get files and samples collection.
    files_collection = db.get_collection(name=Collections.FILES.value.name)
    samples_collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Get number of files and samples for the project.
    project_id_obj = PyObjectId(oid=project_id)
    number_of_files = await files_collection.count_documents(filter={"project_id_list": project_id_obj})
    number_of_samples = await samples_collection.count_documents(filter={"project_id": project_id_obj})

    return {"number_of_files": number_of_files, "number_of_samples": number_of_samples}


async def _get_class_task_detail_information(project_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Get class-related task detail information for a given project.

    Args:
            project_id (str | PyObjectId): The ID of the project to get the class names for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: A dictionary containing class names and their counts in samples for the project.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Get all unique classes from samples.
    project_id_obj = PyObjectId(oid=project_id)
    class_name_list = await collection.distinct(
        key="class_name", filter={"project_id": project_id_obj, "class_name": {"$ne": None}}
    )

    # Get class name histogram.
    class_name_histogram = {}
    for class_name in class_name_list:
        count = await collection.count_documents(filter={"project_id": project_id_obj, "class_name": class_name})
        class_name_histogram[class_name] = count

    return {"class_name_list": class_name_list, "class_name_histogram": class_name_histogram}


async def _get_text_task_detail_information(project_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Get text-related task detail information for a given project.

    Args:
            project_id (str | PyObjectId): The ID of the project to get the class names for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: A dictionary containing total number of lines, words, and characters in text samples for the project.
    """
    # Get sample collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Get total number of lines, words, and characters in text samples for the project.
    project_id_obj = PyObjectId(oid=project_id)
    total_number_of_lines = 0
    total_number_of_words = 0
    total_number_of_characters = 0
    async with collection.find(filter={"project_id": project_id_obj, "text": {"$ne": None}}) as cursor:
        async for sample in cursor:
            text_content = sample.get("text", "")
            total_number_of_lines += text_content.count("\n") + 1
            total_number_of_words += len(text_content.split())
            total_number_of_characters += len(text_content)

    return {
        "total_number_of_lines": total_number_of_lines,
        "total_number_of_words": total_number_of_words,
        "total_number_of_characters": total_number_of_characters,
    }


async def _setup_object_detection_task_detail_model_schema(
    project_id: str | PyObjectId, db: AsyncDatabase
) -> ObjectDetectionTaskDetail:
    """
    Setup function for the object detection task detail model schema.

    Args:
            project_id (str | PyObjectId): The ID of the project to setup the task detail for.
            db (AsyncDatabase): The database instance.

    Returns:
            ObjectDetectionTaskDetail: The setup object detection task detail model schema.
    """
    # Get total number of files and samples for the project.
    number_of_files_and_samples = await _get_number_of_files_and_samples(project_id=project_id, db=db)

    # Get all unique class names in samples for the project.
    class_task_detail_information = await _get_class_task_detail_information(project_id=project_id, db=db)

    # Create task detail model schema with class names and histogram.
    task_detail_model_schema = ObjectDetectionTaskDetail(
        number_of_files=number_of_files_and_samples["number_of_files"],
        number_of_samples=number_of_files_and_samples["number_of_samples"],
        class_name_list=class_task_detail_information["class_name_list"],
        class_name_histogram=class_task_detail_information["class_name_histogram"],
    )

    return task_detail_model_schema


async def _setup_text_classification_task_detail_model_schema(
    project_id: str | PyObjectId, db: AsyncDatabase
) -> TextClassificationTaskDetail:
    """
    Setup function for the text classification task detail model schema.

    Args:
            project_id (str | PyObjectId): The ID of the project to setup the task detail for.
            db (AsyncDatabase): The database instance.

    Returns:
            TextClassificationTaskDetail: The setup text classification task detail model schema.
    """
    # Get total number of files and samples for the project.
    number_of_files_and_samples = await _get_number_of_files_and_samples(project_id=project_id, db=db)

    # Get text-related task detail information for the project.
    text_task_detail_information = await _get_text_task_detail_information(project_id=project_id, db=db)

    # Get all unique class names in samples for the project.
    class_task_detail_information = await _get_class_task_detail_information(project_id=project_id, db=db)

    # Create task detail model schema with class names and histogram.
    task_detail_model_schema = TextClassificationTaskDetail(
        number_of_files=number_of_files_and_samples["number_of_files"],
        number_of_samples=number_of_files_and_samples["number_of_samples"],
        class_name_list=class_task_detail_information["class_name_list"],
        class_name_histogram=class_task_detail_information["class_name_histogram"],
        total_number_of_lines=text_task_detail_information["total_number_of_lines"],
        total_number_of_words=text_task_detail_information["total_number_of_words"],
        total_number_of_characters=text_task_detail_information["total_number_of_characters"],
    )

    return task_detail_model_schema
