"""
Entrypoint used to deploy the AI-Annotator backend API.
"""
import importlib
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo.asynchronous.database import AsyncDatabase

from backend.configs import BackendSettings
from backend.database.configs import DatabaseConfig

# Dynamically import all routers from the routes package
# depending on the API version.
# TODO: router_module = importlib.import_module(f"routes.{BackendSettings.api_version}.routers")

# Startup event to initialize database connection and
# shutdown event to close it.
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize the database client.
    DatabaseConfig.initialize_client(
        uri=BackendSettings.database_uri,
        database_name=BackendSettings.database_name,
        port=BackendSettings.database_port
    )
    yield

    # Close the database client.
    DatabaseConfig.close_client()

# Instantiate the FastAPI application.
app = FastAPI(
    title=BackendSettings.app_name,
    version=BackendSettings.api_version,
    lifespan=lifespan,
    dependencies=[Depends(dependency=DatabaseConfig.get_database)]
)

# Middleware to handle CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=BackendSettings.front_host,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# TODO: Include all routers from the imported module.

# Health check endpoint.
@app.get("/health", response_model=dict, status_code=status.HTTP_200_OK)
async def health_check(db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)) -> dict:
    # Check database status.
    db_status = await db.command("ping")
    return db_status

if __name__ == "__main__":
    uvicorn.run(app, host=BackendSettings.api_host, port=BackendSettings.api_port)