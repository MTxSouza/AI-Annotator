"""
Module with all utilities related to authentication operations.
"""

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from backend.configs import BackendSettings

# Cryptography configurations.
__JWT_ALGORITHM__ = BackendSettings.jwt_algorithm
__SECRET_KEY__ = BackendSettings.secret_key
__ACCESS_TOKEN_EXPIRE_MINUTES__ = BackendSettings.access_token_expire_minutes
__ACCESS_TOKEN_REFRESH_MINUTES__ = BackendSettings.access_token_refresh_minutes
__SALT_LENGTH__ = BackendSettings.salt_length
__PASSWORD_HASH_ALGORITHM__ = BackendSettings.password_hash_algorithm
__PASSWORD_HASH_ITERATIONS__ = BackendSettings.password_hash_iterations
del (
    BackendSettings.jwt_algorithm,
    BackendSettings.secret_key,
    BackendSettings.access_token_expire_minutes,
    BackendSettings.access_token_refresh_minutes,
    BackendSettings.salt_length,
    BackendSettings.password_hash_algorithm,
    BackendSettings.password_hash_iterations,
)  # Remove sensitive information from settings after use.

# Instantiate the OAuth2 scheme.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


# Functions.
def format_hashed_password(hashed_password: str, salt: str) -> str:
    """
    Format a password using `$` as separator.

    Args:
            hashed_password (str): The hashed password to be formatted.
            salt (str): The salt used in the password hashing.

    Returns:
            str: The formatted password.
    """
    return f"{__PASSWORD_HASH_ALGORITHM__}${salt}${__PASSWORD_HASH_ITERATIONS__}${hashed_password}"


def unformat_hashed_password(formatted_password: str) -> tuple[str, str]:
    """
    Unformat a hashed password into its components.

    Args:
            formatted_password (str): The formatted password.

    Returns:
            tuple[str, str]: A tuple containing the salt and the hashed password.
    """
    _, salt, _, hashed_password = formatted_password.split(sep="$", maxsplit=3)
    return salt, hashed_password


def hash_password(password: str, salt: str | None = None) -> str:
    """
    Hash a password and return the hashed formated in the
    format: {algorithm}${salt}${iterations}${hashed_password}.

    Args:
            password (str): The password to be hashed.
            salt (str | None): The salt to be used. If None, a new salt is generated.

    Returns:
            str: The hashed password.
    """
    # Create salt.
    if salt is None:
        salt = os.urandom(__SALT_LENGTH__).hex()

    # Create hash.
    encoded_password = password.encode(encoding="utf-8")
    encoded_salt = salt.encode(encoding="utf-8")

    hashed_password = hashlib.pbkdf2_hmac(
        hash_name=__PASSWORD_HASH_ALGORITHM__,
        password=encoded_password,
        salt=encoded_salt,
        iterations=__PASSWORD_HASH_ITERATIONS__,
    ).hex()

    # Format hashed password with salt.
    hashed_password = format_hashed_password(hashed_password=hashed_password, salt=salt)
    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hashed version.

    Args:
            password (str): The password to be verified.
            hashed_password (str): The hashed password.

    Returns:
            bool: True if the password matches the hash, False otherwise.
    """
    # Unformat hashed password.
    salt, _ = unformat_hashed_password(formatted_password=hashed_password)

    # Hash provided password.
    hashed_provided_password = hash_password(password=password, salt=salt)

    # Check password.
    return hmac.compare_digest(hashed_provided_password, hashed_password)


def generate_single_access_token(data: dict, expires_delta: timedelta | int | None = None) -> str:
    """
    Generate a single JWT access token with an optional expiration time.

    Args:
            data (dict): The data to be included in the token.
            expires_delta (timedelta | int | None): The time delta for the token expiration. If None, the default
            expiration time is used.

    Returns:
            str: The generated JWT access token.
    """
    # Set authentication tokens.
    encoded_token = data.copy()

    if expires_delta is not None:
        if not isinstance(expires_delta, timedelta):
            expires_delta = timedelta(minutes=__ACCESS_TOKEN_EXPIRE_MINUTES__)
        expires_delta = datetime.now(tz=UTC) + expires_delta  # type: ignore
    encoded_token.update({"exp": expires_delta})

    # Create the JWT token.
    token = jwt.encode(claims=encoded_token, key=__SECRET_KEY__, algorithm=__JWT_ALGORITHM__)
    return token


def create_access_token(data: dict) -> dict[str, str]:
    """
    Create both the JWT access token and the refresh token.

    Args:
            data (dict): The data to be included in the token.

    Returns:
            dict[str, str]: A dictionary containing the generated JWT access token and refresh token.
    """
    # Create the JWT tokens.
    expired_token = generate_single_access_token(data=data, expires_delta=__ACCESS_TOKEN_EXPIRE_MINUTES__)
    refresh_token = generate_single_access_token(data=data, expires_delta=__ACCESS_TOKEN_REFRESH_MINUTES__)
    return {"access_token": expired_token, "refresh_token": refresh_token}


def decode_access_token(token: str) -> dict | None:
    """
    Decode a JWT access token.

    Args:
            token (str): The JWT access token to be decoded.

    Returns:
            dict | None: The decoded token data if valid, None otherwise.
    """
    try:
        # Decode the JWT token.
        decoded_token = jwt.decode(token=token, key=__SECRET_KEY__, algorithms=__JWT_ALGORITHM__)
        return decoded_token
    except ExpiredSignatureError:
        throw_bearer_error(message="Token has expired", status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        throw_bearer_error(message="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)
    return None


def throw_bearer_error(message: str, status_code: int) -> None:
    """
    Utility function to throw a 401 Bearer authentication error.

    Args:
            message (str): The error message.
            status_code (int): The HTTP status code.

    Raises:
            HTTPException: The 401 Bearer authentication error.
    """
    raise HTTPException(status_code=status_code, detail=message, headers={"WWW-Authenticate": "Bearer"})
