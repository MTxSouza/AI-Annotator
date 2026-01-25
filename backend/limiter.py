"""
Module used to configure rate limiting for the backend.
"""
from fastapi import FastAPI, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

# Rate limiter instance.
limiter = Limiter(key_func=get_remote_address)  # Simple global limiter for demonstration

# Functions.
def setup_limiter(app: FastAPI) -> None:
    """
    Function to setup the rate limiter for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.state.limiter = limiter
    app.add_exception_handler(status.HTTP_429_TOO_MANY_REQUESTS, _rate_limit_exceeded_handler)
