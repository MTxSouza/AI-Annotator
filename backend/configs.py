"""
Module with configuration for backend.
"""
from pydantic_settings import BaseSettings


# Classes.
class BackendSettings(BaseSettings):
    """
    Class to handle backend settings.
    """

    # Attributes.
    app_name: str = "AI-Annotator"

    api_version: str = "v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    front_host: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    database_uri: str = "mongodb://database"
    database_port: int = 27017
    database_name: str = "ai_annotator_db"

# Instantiate the settings.
BackendSettings = BackendSettings()