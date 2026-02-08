"""
Main module with all schemas used in Samples collection.
"""

from pydantic import BaseModel, Field

from backend.database.enums import PyObjectId
from backend.database.models import CommonRequestModel, CommonResponseModel


# Schemas.
class Sample_DB(CommonResponseModel):
    """
    Sample model in the database.
    """

    # Fields.
    project_id: PyObjectId | str = Field(..., description="The ID of the project the sample belongs to.")


class Sample(BaseModel):
    """
    Sample model.
    """

    # Fields.
    file_id: PyObjectId | str = Field(..., description="The ID of the file associated with the sample.")


class ObjectSample(Sample):
    """
    Object sample model.
    """

    # Fields.
    class_name: str = Field(..., description="The name of the class for the object sample.")


# - Object Detection.
class ObjectDetectionSample(ObjectSample):
    """
    Object detection sample model for API responses.
    """

    # Fields.
    cx: float = Field(
        ..., ge=0.0, le=1.0, description="The x-coordinate of the center of the bounding box (normalized)."
    )
    cy: float = Field(
        ..., ge=0.0, le=1.0, description="The y-coordinate of the center of the bounding box (normalized)."
    )
    width: float = Field(..., ge=0.0, le=1.0, description="The width of the bounding box (normalized).")
    height: float = Field(..., ge=0.0, le=1.0, description="The height of the bounding box (normalized).")


class ObjectDetectionSample_Create(CommonRequestModel, ObjectDetectionSample):
    """
    Object detection sample model for creating new samples.
    """

    pass


class ObjectDetectionSample_DB(Sample_DB, ObjectDetectionSample):
    """
    Object detection sample model in the database.
    """

    pass
