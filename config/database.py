"""
This file handles the helper methods to read the configuration
of the database.

Functions:
    database_uri(): This method will read the database URI from the
        `.env` file and return it as a string.

Author:
    Jiacheng Zhao (John)
"""
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), 'secret', '.env')

load_dotenv(dotenv_path)

def database_uri() -> str:
    """This method will read the database URI from the
    environment and return it as a string.
    
    
    Args:
        None.
    
    
    Returns:
        str: The database URI from the environment.
        
    
    Raises:
        KeyError: If the `DATABASE_URI` key is not found in the environment.
    """
    obtained_database_uri = os.getenv("DATABASE_URI")
    if obtained_database_uri is None:
        raise KeyError("DATABASE_URI not found in the environment.")
    return obtained_database_uri
