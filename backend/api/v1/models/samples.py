"""
Main module with all schemas used in Samples collection.
"""

from pydantic import Field

from backend.database.enums import PyObjectId
from backend.database.models import CommonResponseModel


# Schemas.
class __Sample(CommonResponseModel):
    """
    Sample model in the database.
    """

    # Fields.
    project_id: PyObjectId | str = Field(..., description="The ID of the project the sample belongs to.")
    file_id: PyObjectId | str = Field(..., description="The ID of the file associated with the sample.")


class ObjectSample_DB(__Sample):
    """
    Object sample model in the database.
    """

    # Fields.
    class_name: str = Field(..., description="The name of the class for the object sample.")


# - Object Detection.
class ObjectDetectionSample_DB(ObjectSample_DB):
    """
    Object detection sample model in the database.
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


class ObjectDetectionSample(ObjectDetectionSample_DB):
    """
    Object detection sample model for API responses.
    """

    pass
