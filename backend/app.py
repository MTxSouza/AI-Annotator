"""
Entrypoint used to deploy the AI-Annotator backend API.
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from pymongo.asynchronous.database import AsyncDatabase

from backend.configs import BackendSettings, setup_routers
from backend.database.configs import DatabaseConfig
from backend.limiter import limiter, setup_limiter


# Startup event to initialize database connection and
# shutdown event to close it.
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize the database client.
    await DatabaseConfig.initialize_client(
        uri=BackendSettings.database_uri,
        database_name=BackendSettings.database_name,
        port=BackendSettings.database_port
    )
    yield

    # Close the database client.
    await DatabaseConfig.close_client()

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

# Setup rate limiter.
setup_limiter(app=app)

# Include all routers from the imported module.
setup_routers(app=app, api_version=BackendSettings.api_version)

# Health check endpoint.
@app.get("/health", response_model=dict, status_code=status.HTTP_200_OK)
@limiter.limit(limit_value="10/minute")
async def health_check(
    request: Request,
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> dict:
    # Check database status.
    db_status = await db.command("ping")
    return db_status

if __name__ == "__main__":
    uvicorn.run(app, host=BackendSettings.api_host, port=BackendSettings.api_port)