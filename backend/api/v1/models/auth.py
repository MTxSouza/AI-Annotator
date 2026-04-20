"""
Main module with all schemas used in Authentication.
"""

from pydantic import BaseModel, Field


# Schemas.
class Token(BaseModel):
    """
    Token model.
    """

    # Fields.
    access_token: str = Field(..., description="The access token.")
    token_type: str | None = Field(default="bearer", description="The type of the token.")
