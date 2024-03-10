"""
This file handles the helper methods to read 
the JWT configuration provided by the environment.

Functions:
    jwt_private_key(file_path: str) -> str: This method will read the JWT private key from the file
        and return it as a string.
    jwt_public_key(file_path: str) -> str: This method will read the JWT public key from the file
        and return it as a string.
    jwt_algorithm() -> str: This method will read the JWT algorithm used to sign the token. Right now,
        it is set to RS256.
    
Author:
    Jiacheng Zhao (John)
"""
import os


def jwt_private_key(file_path="jwt_private.pem") -> str:
    """This method will read the JWT secret from the file
    and return it as a string.
    
    
    Args:
        file_path (str): The path to the JWT secret file.
            Make sure the file is in the `config/secret` directory.
    
    
    Returns:
        str: The JWT secret.
    
    
    Raises:
        FileNotFoundError: If the file is not found.
    """
    path = os.path.join(os.path.dirname(__file__), "secret", file_path)
    with open(path, "r") as file:
        return file.read()
    

def jwt_public_key(file_path="jwt_public.pem") -> str:
    """This method will read the JWT public key from the file
    and return it as a string.
    
    
    Args:
        file_path (str): The path to the JWT public key file.
            Make sure the file is in the `config/secret` directory.
    
    
    Returns:
        str: The JWT public key.
    
    
    Raises:
        FileNotFoundError: If the file is not found.
    """
    path = os.path.join(os.path.dirname(__file__), "secret", file_path)
    with open(path, "r") as file:
        return file.read()


def jwt_algorithm() -> str:
    """This method will read the JWT algorithm
    
    
    Args:
        None.
    
    
    Returns:
        str: The JWT algorithm.
    """
    return "RS256"