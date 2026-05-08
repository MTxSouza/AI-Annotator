"""
Module with configuration for backend.
"""

import importlib
import os
import pkgutil

from fastapi import FastAPI
from pydantic_settings import BaseSettings


# Functions.
def setup_routers(app: FastAPI, api_version: str) -> None:
    """
    Function to setup routers for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
        api_version (str): The API version to use for routing.
    """
    # Dynamically import all routers from the routes package
    # depending on the API version.
    module_path = f"backend.api.{api_version}.routers"
    try:
        router_module = importlib.import_module(name=module_path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Module {module_path} not found.")

    # Include all routers in the FastAPI application.
    for _, module_name, _ in pkgutil.iter_modules(path=router_module.__path__):
        # Skip special modules.
        if module_name == "__init__" or module_name.startswith("_"):
            continue

        # Import the module.
        internal_module_path = f"{module_path}.{module_name}"
        internal_module = importlib.import_module(name=internal_module_path)

        # Look for the router attribute and include it.
        if hasattr(internal_module, "router"):
            app.include_router(router=internal_module.router)


# Classes.
class BackendSettingsModel(BaseSettings):
    """
    Class to handle backend settings.
    """

    # Attributes.
    app_name: str = "AI-Annotator"

    api_version: str = "v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    front_host: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    database_uri: str = "mongodb://database"
    database_port: int = 27017
    database_name: str = os.getenv("AI_ANNOTATOR_DATABASE_NAME", "ai_annotator_db")

    redis_uri: str = "redis://redis"
    redis_port: int = 6379
    redis_db: int = 0

    jwt_algorithm: str = "HS256"
    secret_key: str = os.environ["AI_ANNOTATOR_SECRET_KEY"]  # Mandatory environment variable.
    access_token_expire_minutes: int = 30
    access_token_refresh_minutes: int = 60 * 24  # 1 day
    salt_length: int = 16
    password_hash_algorithm: str = "sha256"
    password_hash_iterations: int = 100000

    static_file_directory: str = "/app/storage"
    max_upload_file_size: int = 10 * 1024**3  # 10 GB

    # Properties.
    @property
    def api_root_path(self) -> str:
        """
        Property to get the API root path.
        """
        return f"/api/{self.api_version}"


# Instantiate the settings.
BackendSettings = BackendSettingsModel()
