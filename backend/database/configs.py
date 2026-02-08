"""
Main module with all database configurations.
"""

from dataclasses import dataclass
from enum import Enum

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


# Global variables.
@dataclass
class _IndexConfig:
    """
    Class to handle index configuration.
    """

    name: str
    is_indexed: bool = False
    is_unique: bool = False


@dataclass
class _CollectionConfig:
    """
    Class to handle collection configuration.
    """

    name: str
    index_configs: list[_IndexConfig] | None = []


class Collections(Enum):
    """
    Enum to handle collection names.
    """

    PROJECTS = _CollectionConfig(
        name="projects", index_configs=[_IndexConfig(name="name", is_indexed=True, is_unique=True)]
    )
    TASK_CONFIGS = _CollectionConfig(
        name="task_configs", index_configs=[_IndexConfig(name="project_id", is_unique=True)]
    )
    FILES = _CollectionConfig(
        name="files",
        index_configs=[
            _IndexConfig(name="file_hash", is_indexed=True, is_unique=True),
            _IndexConfig(name="filename", is_indexed=True, is_unique=True),
        ],
    )
    SAMPLES = _CollectionConfig(
        name="samples",
    )


# Classes.
class DatabaseConfig:
    """
    Class to handle database configurations.
    """

    # Attributes.
    __client: AsyncMongoClient = None
    __database_name: str = None

    # Class methods.
    @classmethod
    async def initialize_client(cls, uri: str, database_name: str, port: int = 27017) -> None:
        """
        Method to initialize the database client.

        Args:
            uri (str): The database URI.
            database_name (str): The name of the database.
            port (int): The database port. (Default: 27017)
        """
        # Initialize the MongoDB client.
        cls.__client = AsyncMongoClient(host=uri, port=port)
        cls.__database_name = database_name

        # Setup collections.
        db = cls.get_database()
        for collection_config in Collections:
            collection = db.get_collection(name=collection_config.value.name)
            for index_config in collection_config.value.index_configs:
                if index_config.is_indexed or index_config.is_unique:
                    await collection.create_index(
                        keys=[(index_config.name, 1)], unique=index_config.is_unique, background=True
                    )

    @classmethod
    async def close_client(cls) -> None:
        """
        Method to close the database client.
        """
        # Check if the client is initialized.
        cls._check_client_initialized()

        # Close the MongoDB client.
        await cls.__client.close()
        cls.__client = None
        cls.__database_name = None

    @classmethod
    def _check_client_initialized(cls) -> None:
        """
        Method to check if the database client is initialized.

        Raises:
            Exception: If the database client is not initialized.
        """
        if cls.__client is None:
            raise Exception("Database client is not initialized.")

    @classmethod
    def get_database(cls) -> AsyncDatabase:
        """
        Method to get the database connection.

        Returns:
            AsyncDatabase: The database connection.
        """
        # Check if the client is initialized.
        cls._check_client_initialized()

        # Return the database connection.
        return cls.__client.get_database(name=cls.__database_name)

    @classmethod
    async def _drop_database(cls) -> None:
        """
        Method to drop the database. (For testing purposes only)
        """
        # Check if the client is initialized.
        cls._check_client_initialized()

        # Drop the database.
        await cls.__client.drop_database(name_or_database=cls.__database_name)

    # Properties.
    @property
    def client(self) -> AsyncMongoClient:
        """
        Property to get the database client.

        Returns:
            AsyncMongoClient: The database client.
        """
        # Check if the client is initialized.
        self._check_client_initialized()

        # Return the database client.
        return self.__client

    @property
    def database_name(self) -> str:
        """
        Property to get the database name.

        Returns:
            str: The database name.
        """
        return self.__database_name
