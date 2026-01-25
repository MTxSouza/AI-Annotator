"""
Main module with all database configurations.
"""
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


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
    def initialize_client(cls, uri: str, database_name: str, port: int = 27017) -> None:
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

    @classmethod
    def close_client(cls) -> None:
        """
        Method to close the database client.
        """
        # Check if the client is initialized.
        cls._check_client_initialized()

        # Close the MongoDB client.
        cls.__client.close()
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
    def _drop_database(cls) -> None:
        """
        Method to drop the database. (For testing purposes only)
        """
        # Check if the client is initialized.
        cls._check_client_initialized()

        # Drop the database.
        cls.__client.drop_database(name=cls.__database_name)

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
