"""
Module with common database models inherited by all API models.
"""

from pydantic import BaseModel, ConfigDict, Field

from backend.database.enums import PyDateTime, PyObjectId
from backend.database.utils import get_current_datetime


# Schemas.
class _TimestampModel(BaseModel):
    """
    Base timestamp model inherited by all API models.
    """

    # Fields.
    created_at: PyDateTime = Field(default_factory=get_current_datetime, description="The creation timestamp.")
    updated_at: PyDateTime = Field(default_factory=get_current_datetime, description="The last update timestamp.")


class CommonResponseModel(_TimestampModel):
    """
    Common response model inherited by all API response models.
    """

    # Fields.
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    # Config.
    model_config = ConfigDict(populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)


class CommonRequestModel(_TimestampModel):
    """
    Common request model inherited by all API request models.
    """

    # Config.
    model_config = ConfigDict(extra="forbid")


class CommonUpdateModel(_TimestampModel):
    """
    Common update model inherited by all API update models.
    """

    # To be excluded.
    created_at: PyDateTime | None = Field(default=None, exclude=True)  # type: ignore

    # Config.
    model_config = ConfigDict(extra="forbid")
