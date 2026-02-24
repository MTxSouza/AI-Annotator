"""
Module with all utilities related to task configuration operations.
"""

from collections.abc import Callable

from fastapi import status
from fastapi.exceptions import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.task_details import (
    AudioTranscriptionTaskDetail,
    ObjectDetectionTaskDetail,
    Task,
    TextClassificationTaskDetail,
)
from backend.database.configs import Collections
from backend.database.enums import FileFormat, PyObjectId
from backend.database.enums import Task as TaskType


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
        TaskType.OBJECT_DETECTION.value: "image",
        TaskType.IMAGE_CLASSIFICATION.value: "image",
        TaskType.IMAGE_CAPTION.value: "image",
        TaskType.OBJECT_CAPTION.value: "image",
        TaskType.TEXT_CLASSIFICATION.value: "text",
        TaskType.TEXT_TAGGING.value: "text",
        TaskType.AUDIO_CLASSIFICATION.value: "audio",
        TaskType.AUDIO_TRANSCRIPTION.value: "audio",
    }
    return task_file_map.get(task)


def get_task_description(task: str) -> str | None:
    """
    Get the description for a given task.

    Args:
            task (str): The task to get the description for.

    Returns:
            str | None: The description for the task, or None if not found.
    """
    task_description_map = {
        TaskType.OBJECT_DETECTION.value: "Draw a bounding box around the object on an image and label it with the "
        "appropriate category or class name.",
        TaskType.IMAGE_CLASSIFICATION.value: "Label the image with the appropriate category or class name.",
        TaskType.IMAGE_CAPTION.value: "Create a descriptive caption for the image.",
        TaskType.OBJECT_CAPTION.value: "Draw a bounding box around the object on an image and create a descriptive "
        "caption for it.",
        TaskType.TEXT_CLASSIFICATION.value: "Label the text with the appropriate category or class name.",
        TaskType.TEXT_TAGGING.value: "Tag sentences or words in the text with the appropriate category or class name.",
        TaskType.AUDIO_CLASSIFICATION.value: "Label the audio clip with the appropriate category or class name.",
        TaskType.AUDIO_TRANSCRIPTION.value: "Transcribe the audio clip into text.",
    }
    return task_description_map.get(task)


def get_task_detail_builder_function(task: str) -> Callable | None:
    """
    Get the associated task detail builder function for a given task.

    Args:
            task (str): The task to get the detail builder function for.

    Returns:
            Callable | None: The associated task detail builder function for the task, or None if not found.
    """
    task_detail_builder_function_map = {
        TaskType.OBJECT_DETECTION.value: _setup_object_detection_task_detail_model_schema,
        TaskType.IMAGE_CLASSIFICATION.value: None,
        TaskType.IMAGE_CAPTION.value: None,
        TaskType.OBJECT_CAPTION.value: None,
        TaskType.TEXT_CLASSIFICATION.value: _setup_text_classification_task_detail_model_schema,
        TaskType.TEXT_TAGGING.value: None,
        TaskType.AUDIO_CLASSIFICATION.value: None,
        TaskType.AUDIO_TRANSCRIPTION.value: _setup_audio_transcription_task_detail_model_schema,
    }
    return task_detail_builder_function_map.get(task)


def get_tasks() -> list[Task]:
    """
    Get a list of all available and already implemented tasks to be used in the application.

    Returns:
            list[Task]: A list of all available tasks.
    """
    # Get all tasks from the TaskType enum.
    task_list = [task for task in TaskType]

    # Build list of Task models.
    available_task_list = []
    for task in task_list:
        task_name = task.value

        # Get task file.
        task_file = get_task_file(task=task_name)

        # Get task description.
        description = get_task_description(task=task_name)

        # Check content.
        if not (task_file and description and get_task_detail_builder_function(task=task_name)):
            continue

        # Get available file formats for the task.
        file_format_map = {
            "image": FileFormat.get_image_formats(),
            "text": FileFormat.get_text_formats(),
            "audio": FileFormat.get_audio_formats(),
        }
        file_format_list = file_format_map.get(task_file, [])

        # Create Task model and add to list.
        task_model = Task(name=task, description=description, file_format_list=file_format_list)
        available_task_list.append(task_model)

    return available_task_list


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
        TaskType.OBJECT_DETECTION.value: -1,
        TaskType.IMAGE_CLASSIFICATION.value: 1,
        TaskType.IMAGE_CAPTION.value: -1,
        TaskType.OBJECT_CAPTION.value: -1,
        TaskType.TEXT_CLASSIFICATION.value: 1,
        TaskType.TEXT_TAGGING.value: -1,
        TaskType.AUDIO_CLASSIFICATION.value: 1,
        TaskType.AUDIO_TRANSCRIPTION.value: 1,
    }
    return task_samples_per_file_map.get(task)


async def setup_task_detail(task: TaskType, project_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Utility function to setup the task configuration based on the task type.

    Args:
            task (TaskType): The task type.
            project_id (str | PyObjectId): The ID of the project to setup the task detail for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: The task configuration template.
    """
    # Fix task enum if needed.
    if isinstance(task, TaskType):
        task_str = task.value
    else:
        task_str = task

    # Get the task detail class based on the task type.
    task_detail_instance_dict = await setup_task_detail_model_schema(task=task_str, project_id=project_id, db=db)

    if not task_detail_instance_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task detail setup is not implemented for task: {task_str}"
        )

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
    task_detail_setup_function = get_task_detail_builder_function(task=task)
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


async def _get_audio_task_detail_information(project_id: str | PyObjectId, db: AsyncDatabase) -> dict:
    """
    Get audio-related task detail information for a given project.

    Args:
            project_id (str | PyObjectId): The ID of the project to get the audio-related information for.
            db (AsyncDatabase): The database instance.

    Returns:
            dict: A dictionary containing total duration of audio samples for the project.
    """
    # Get file collection.
    collection = db.get_collection(name=Collections.FILES.value.name)

    # Get total duration of audio samples for the project.
    project_id_obj = PyObjectId(oid=project_id)
    total_duration_in_seconds = 0
    async with collection.find(
        filter={"project_id_list": project_id_obj, "duration_in_seconds": {"$ne": None}}
    ) as cursor:
        async for file in cursor:
            duration_in_seconds = file.get("duration_in_seconds", 0)
            total_duration_in_seconds += duration_in_seconds

    return {"total_duration_in_seconds": total_duration_in_seconds}


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


async def _setup_audio_transcription_task_detail_model_schema(
    project_id: str | PyObjectId, db: AsyncDatabase
) -> AudioTranscriptionTaskDetail:
    """
    Setup function for the audio transcription task detail model schema.

    Args:
            project_id (str | PyObjectId): The ID of the project to setup the task detail for.
            db (AsyncDatabase): The database instance.

    Returns:
            AudioTranscriptionTaskDetail: The setup audio transcription task detail model schema.
    """
    # Get total number of files and samples for the project.
    number_of_files_and_samples = await _get_number_of_files_and_samples(project_id=project_id, db=db)

    # Get text-related task detail information for the project.
    text_task_detail_information = await _get_text_task_detail_information(project_id=project_id, db=db)

    # Get audio-related task detail information for the project.
    audio_task_detail_information = await _get_audio_task_detail_information(project_id=project_id, db=db)

    # Create task detail model schema with total duration of audio samples.
    task_detail_model_schema = AudioTranscriptionTaskDetail(
        number_of_files=number_of_files_and_samples["number_of_files"],
        number_of_samples=number_of_files_and_samples["number_of_samples"],
        total_number_of_lines=text_task_detail_information["total_number_of_lines"],
        total_number_of_words=text_task_detail_information["total_number_of_words"],
        total_number_of_characters=text_task_detail_information["total_number_of_characters"],
        total_duration_in_seconds=audio_task_detail_information["total_duration_in_seconds"],
    )

    return task_detail_model_schema
