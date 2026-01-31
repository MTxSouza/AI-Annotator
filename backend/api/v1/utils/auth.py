"""
Module with all utilities related to authentication operations.
"""
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.configs import BackendSettings

# Cryptography configurations.
__JWT_ALGORITHM__ = BackendSettings.jwt_algorithm
__SECRET_KEY__ = BackendSettings.secret_key
__ACCESS_TOKEN_EXPIRE_MINUTES__ = BackendSettings.access_token_expire_minutes
del BackendSettings.jwt_algorithm, BackendSettings.secret_key # Remove sensitive information from settings after use.

# Instantiate the password context for hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Instantiate the OAuth2 scheme.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# Functions.
def hash_password(password: str) -> str:
    """
    Hash a password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(secret=password)

def check_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hashed version.

    Args:
        password (str): The password to be verified.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(secret=password, hash=hashed_password)

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to be included in the token.

    Returns:
        str: The generated JWT access token.
    """
    # Set expiration time.
    encoded_token = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=__ACCESS_TOKEN_EXPIRE_MINUTES__)
    encoded_token.update({"exp": expire})

    # Create the JWT token.
    token = jwt.encode(claims=encoded_token, key=__SECRET_KEY__, algorithm=__JWT_ALGORITHM__)
    return token

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
    except JWTError:
        return None
