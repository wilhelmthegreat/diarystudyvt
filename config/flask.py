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


def flask_use_ssl() -> bool:
    """This method will read the use SSL flag from the `.env`
    file and return it as a boolean to enable or disable Flask's
    SSL mode.
    
    
    Args:
        None.
    
    
    Returns:
        bool: The use SSL flag from the environment.
    
    
    Raises:
        KeyError: If the `SSL_ENABLED` key is not found in the environment.
    """
    obtained_use_ssl = os.getenv("SSL_ENABLED")
    if obtained_use_ssl is None:
        return False # Temporary put to False to avoid error
        # raise KeyError("SSL_ENABLED not found in the environment.")
    return obtained_use_ssl.upper() == "TRUE"


def flask_cert_path() -> str:
    """This method will read the certificate path from the `.env`
    file and return it as a string.
    
    
    Args:
        None.
    
    
    Returns:
        str: The certificate path from the environment.
    
    
    Raises:
        KeyError: If the `SERVER_CERT` key is not found in the environment.
    """
    obtained_cert_path = os.getenv("SERVER_CERT")
    if obtained_cert_path is None:
        raise KeyError("SERVER_CERT not found in the environment.")
    return obtained_cert_path


def flask_key_path() -> str:
    """This method will read the key path from the `.env`
    file and return it as a string.
    
    
    Args:
        None.
    
    
    Returns:
        str: The key path from the environment.
    
    
    Raises:
        KeyError: If the `SERVER_KEY` key is not found in the environment.
    """
    obtained_key_path = os.getenv("SERVER_KEY")
    if obtained_key_path is None:
        raise KeyError("SERVER_KEY not found in the environment.")
    return obtained_key_path


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
