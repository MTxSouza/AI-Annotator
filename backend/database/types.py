"""
Module with custom types for database operations.
"""
from enum import Enum

from bson import ObjectId
from pydantic.json_schema import GetJsonSchemaHandler, JsonSchemaValue


# Types.
class PyObjectId(ObjectId):
    """
    Custom type to handle ObjectId in Pydantic models.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: JsonSchemaValue, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class TaskType(str, Enum):
    """
    Enum for task types.
    """
    OBJECT_DETECTION = "object_detection"
