"""
Module with all utilities related to sample operations.
"""

from pymongo.asynchronous.database import AsyncDatabase

from backend.database.configs import Collections


# Functions.
async def get_samples(limit: int, offset: int, db: AsyncDatabase) -> list[dict]:
    """
    Get all samples.

    Args:
            limit (int): The maximum number of samples to return.
            offset (int): The number of samples to skip before starting to collect the result set.
            db (AsyncDatabase): The database instance.

    Returns:
            list: List of all samples.
    """
    # Get samples collection.
    collection = db.get_collection(name=Collections.SAMPLES.value.name)

    # Query samples.
    cursor = collection.find().skip(skip=offset).limit(limit=limit)
    samples = await cursor.to_list()

    return samples
