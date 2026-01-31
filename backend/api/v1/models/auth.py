"""
Main module with all schemas used in Authentication.
"""
from typing import Optional

from pydantic import BaseModel, Field


# Schemas.
class Token(BaseModel):
    """
    Token model.
    """
    # Fields.
    access_token: str = Field(..., description="The access token.")
    token_type: Optional[str] = Field(default="bearer", description="The type of the token.")
