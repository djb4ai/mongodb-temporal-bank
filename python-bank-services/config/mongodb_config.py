import os
from pymongo import MongoClient

class MongodbConfig:
    """
    MongoDB configuration class similar to the Java MongodbConfig.
    """
    CONN_STRING_ENV_VARNAME = "MONGO_CONNECTION_STRING"
    CONNECTION_STRING = "mongodb+srv://cluster0.4r3jo.mongodb.net?appName=devrel.integration.mcp-atlas"
    DATABASE_NAME = "bankingdemo"

    @staticmethod
    def get_database():
        """
        Returns the database with the default name, accessible through a
        connection string defined through an environment variable.
        """
        return MongodbConfig.get_database_with_params(MongodbConfig.DATABASE_NAME, MongodbConfig.CONNECTION_STRING)

    @staticmethod
    def get_database_with_params(database_name, connection_string):
        """
        Returns the database with the specified name, accessible through the
        specified connection string.
        
        Args:
            database_name: The name of the database to connect to
            connection_string: Specifies details for connecting to that database
        Returns:
            The MongoDB database corresponding to the input parameters
        """
        client = MongoClient(connection_string)
        return client[database_name]