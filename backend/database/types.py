"""
Module with custom types for database operations.
"""
from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema


# Types.
def validate_py_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(oid=v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(func=validate_py_object_id),
    PlainSerializer(func=lambda oid: str(oid), return_type=str),
    WithJsonSchema(json_schema={"type": "string"})
]
PyDateTime = Annotated[datetime, PlainSerializer(func=lambda dt: dt.isoformat())]

class Task(str, Enum):
    """
    Enum for tasks.
    """
    OBJECT_DETECTION = "Object Detection"
