"""
This file contains the flask application configuration.


Functions:
    bind_host(): This method will read the bind host from the `.env` file and
        return it as a string.
    flask_debug(): This method will read the debug flag from the `.env`
        file and return it as a boolean to enable or disable Flask's
        debug mode.
    port(): This method will read the port from the `.env` file and return
        it as an integer.
"""
from dotenv import load_dotenv
import os


dotenv_path = os.path.join(os.path.dirname(__file__), 'secret', '.env')

load_dotenv(dotenv_path, override=True)


def bind_host() -> str:
    """This method will read the bind host from the `.env` file and
    return it as a string.
    
    
    Args:
        None.
    
    
    Returns:
        str: The bind host from the environment.
    
    
    Raises:
        KeyError: If the `HOST` key is not found in the environment.
    """
    obtained_bind_host = os.getenv("FLASK_HOST")
    if obtained_bind_host is None:
        raise KeyError("FLASK_HOST not found in the environment.")
    return obtained_bind_host


def flask_debug() -> bool:
    """This method will read the debug flag from the `.env`
    file and return it as a boolean to enable or disable Flask's
    debug mode.
    
    
    Args:
        None.
    
    
    Returns:
        bool: The debug flag from the environment.
    
    
    Raises:
        KeyError: If the `FLASK_DEBUG` key is not found in the environment.
    """
    obtained_debug = os.getenv("FLASK_DEBUG")
    if obtained_debug is None:
        raise KeyError("FLASK_DEBUG not found in the environment.")
    return obtained_debug.upper() == "TRUE"


def port() -> int:
    """This method will read the port from the `.env` file and return
    it as an integer.
    
    
    Args:
        None.
    
    
    Returns:
        int: The port from the environment.
    
    
    Raises:
        KeyError: If the `PORT` key is not found in the environment.
    """
    obtained_port = os.getenv("PORT")
    if obtained_port is None:
        raise KeyError("PORT not found in the environment.")
    return int(obtained_port)
