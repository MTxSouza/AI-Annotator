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
    module_path = "backend.api.%s.routers" % api_version
    try:
        router_module = importlib.import_module(name=module_path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Module %s not found." % module_path)

    # Include all routers in the FastAPI application.
    for _, module_name, _ in pkgutil.iter_modules(path=router_module.__path__):

        # Skip special modules.
        if module_name == "__init__" or module_name.startswith("_"):
            continue

        # Import the module.
        internal_module_path = "%s.%s" % (module_path, module_name)
        internal_module = importlib.import_module(name=internal_module_path)

        # Look for the router attribute and include it.
        if hasattr(internal_module, "router"):
            app.include_router(router=internal_module.router)

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
    database_name: str = os.getenv("AI_ANNOTATOR_DATABASE_NAME", "ai_annotator_db")

    jwt_algorithm: str = "HS256"
    secret_key: str = os.getenv("AI_ANNOTATOR_SECRET_KEY", "your_default_secret_key")
    access_token_expire_minutes: int = 60 * 24  # 1 day
    salt_length: int = 16
    password_hash_algorithm: str = "sha256"
    password_hash_iterations: int = 100000

    # Properties.
    @property
    def api_root_path(self) -> str:
        """
        Property to get the API root path.
        """
        return "/api/%s" % self.api_version

# Instantiate the settings.
BackendSettings = BackendSettings()