"""
Module with all endpoints related to authentication operations.
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.asynchronous.database import AsyncDatabase

from backend.api.v1.models.auth import Token
from backend.api.v1.utils.auth import check_password, create_access_token, refresh_tokens, set_auth_cookies
from backend.api.v1.utils.projects import get_project_by_id
from backend.database.configs import DatabaseConfig
from backend.limiter import limiter

# Instantiate the router.
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# Endpoints.
@router.post(path="/token", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def authenticate_access_token(
    request: Request,
    response: Response,
    auth_form: OAuth2PasswordRequestForm = Depends(dependency=OAuth2PasswordRequestForm),
    db: AsyncDatabase = Depends(dependency=DatabaseConfig.get_database),
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

    # Check if the project is not private.
    if not project["hashed_password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project is not private")

    # Check if the password is correct.
    if not check_password(password=password, hashed_password=project["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create access token.
    token_data = create_access_token(data={"sub": project_id})
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)

    return Token(access_token=access_token, token_type="bearer")


@router.post(path="/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_access_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Token:
    """
    Endpoint to issue a new access token using the refresh token cookie.
    """
    # Check if the refresh token is provided.
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")

    # Refresh the access token.
    new_access_token = refresh_tokens(refresh_token=refresh_token)
    set_auth_cookies(response, access_token=new_access_token)

    return Token(access_token=new_access_token, token_type="bearer")


@router.post(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """
    Endpoint to clear the auth cookies, effectively logging the project out.
    """
    # Clear the auth cookies.
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
