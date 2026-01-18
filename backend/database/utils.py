"""
Module with basic functions to be used in database operations.
"""
from datetime import datetime, timezone


# Functions.
def get_current_datetime() -> datetime:
    """
    Function to get the current date and time.

    Returns:
        datetime: The current date and time.
    """
    return datetime.now(tz=timezone.utc)
