"""
Main module with all schemas used in Samples collection.
"""

from pydantic import Field

from backend.database.enums import PyObjectId
from backend.database.models import CommonModel, CommonRequestModel, CommonResponseModel


# Schemas.
class _Sample(CommonModel):
    """
    Schema for a sample.
    """

    project_id: str | PyObjectId = Field(..., description="ID of the project associated with the sample.")
    file_id: str | PyObjectId = Field(..., description="ID of the file associated with the sample.")


class _SampleDB(CommonResponseModel, _Sample):
    """
    Schema for a sample in the database.
    """

    pass


class _SampleCreate(_Sample, CommonRequestModel):
    """
    Schema for creating a sample.
    """

    pass


class _SampleUpdate(_Sample):
    """
    Schema for updating a sample.
    """

    project_id: str | PyObjectId | None = Field(default=None, exclude=True)  # type: ignore
    file_id: str | PyObjectId | None = Field(default=None, exclude=True)  # type: ignore


# - Schemas for different sample types.
class _VisualLocationSample(_Sample):
    """
    Schema for a visual location sample.
    """

    cx: float = Field(..., description="X-coordinate of the center of the bounding box.")
    cy: float = Field(..., description="Y-coordinate of the center of the bounding box.")
    width: float = Field(..., description="Width of the bounding box.")
    height: float = Field(..., description="Height of the bounding box.")


class _VisualLocationSampleUpdate(_SampleUpdate):
    """
    Schema for updating a visual location sample.
    """

    cx: float | None = Field(default=None)
    cy: float | None = Field(default=None)
    width: float | None = Field(default=None)
    height: float | None = Field(default=None)


class _ClassSample(_Sample):
    """
    Schema for a class sample.
    """

    class_name: str = Field(..., description="Name of the class associated with the sample.")


class _ClassSampleUpdate(_SampleUpdate):
    """
    Schema for updating a class sample.
    """

    class_name: str | None = Field(default=None)


class _TextSample(_Sample):
    """
    Schema for a text sample.
    """

    text: str = Field(..., description="Text associated with the sample.")


class _TextSampleUpdate(_SampleUpdate):
    """
    Schema for updating a text sample.
    """

    text: str | None = Field(default=None)


# - Image Task Samples.
# * Image Classification Sample.
class _ImageClassificationSample(_ClassSample):
    """
    Schema for an image classification sample.
    """

    pass


class ImageClassificationSample(_SampleDB, _ImageClassificationSample):
    """
    Schema for an image classification sample.
    """

    pass


class ImageClassificationSampleCreate(_SampleCreate, _ImageClassificationSample):
    """
    Schema for creating an image classification sample.
    """

    pass


class ImageClassificationSampleUpdate(_ClassSampleUpdate):
    """
    Schema for updating an image classification sample.
    """

    pass


# * Object Detection Sample.
class _ObjectDetectionSample(_ClassSample, _VisualLocationSample):
    """
    Schema for an object detection sample.
    """

    pass


class ObjectDetectionSample(_SampleDB, _ObjectDetectionSample):
    """
    Schema for an object detection sample.
    """

    pass


class ObjectDetectionSampleCreate(_SampleCreate, _ObjectDetectionSample):
    """
    Schema for creating an object detection sample.
    """

    pass


class ObjectDetectionSampleUpdate(_ClassSampleUpdate, _VisualLocationSampleUpdate):
    """
    Schema for updating an object detection sample.
    """

    pass


# * Image Caption Sample.
class _ImageCaptionSample(_TextSample):
    """
    Schema for an image caption sample.
    """

    pass


class ImageCaptionSample(_SampleDB, _ImageCaptionSample):
    """
    Schema for an image caption sample.
    """

    pass


class ImageCaptionSampleCreate(_SampleCreate, _ImageCaptionSample):
    """
    Schema for creating an image caption sample.
    """

    pass


class ImageCaptionSampleUpdate(_TextSampleUpdate):
    """
    Schema for updating an image caption sample.
    """

    pass


# * Object Caption Sample.
class _ObjectCaptionSample(_TextSample, _VisualLocationSample):
    """
    Schema for an object caption sample.
    """

    pass


class ObjectCaptionSample(_SampleDB, _ObjectCaptionSample):
    """
    Schema for an object caption sample.
    """

    pass


class ObjectCaptionSampleCreate(_SampleCreate, _ObjectCaptionSample):
    """
    Schema for creating an object caption sample.
    """

    pass


class ObjectCaptionSampleUpdate(_TextSampleUpdate, _VisualLocationSampleUpdate):
    """
    Schema for updating an object caption sample.
    """

    pass
