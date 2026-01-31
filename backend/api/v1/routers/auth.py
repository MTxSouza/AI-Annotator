"""
Module with all endpoints related to authentication operations.
"""
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.auth import Token
from backend.api.v1.utils.auth import check_password, create_access_token
from backend.api.v1.utils.projects import get_project_by_id
from backend.database.configs import DatabaseConfig

# Instantiate the router.
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    dependencies=[Depends(dependency=DatabaseConfig.get_database), Depends(dependency=OAuth2PasswordRequestForm)]
)

# Endpoints.
@router.post(path="/token", response_model=Token, status_code=status.HTTP_200_OK)
async def authenticate_access_token(
    auth_form: OAuth2PasswordRequestForm = Depends(dependency=OAuth2PasswordRequestForm),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database)
    ) -> Token:
    """
    Endpoint to authenticate and provide an access token to 
    access protected project.
    """
    # Get credentials.
    project_id = auth_form.username
    password = auth_form.password

    # Check if the project exists.
    project = await get_project_by_id(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if the project is private.
    if not project["is_private"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project is not private")

    # Check if the password is correct.
    if not check_password(password=password, hashed_password=project["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create access token.
    access_token = create_access_token(data={"sub": project_id})

    # Return access token.
    return Token(access_token=access_token, token_type="bearer")
