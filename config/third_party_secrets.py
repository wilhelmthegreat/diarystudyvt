"""
This file handles the helper methods to read the configuration
provided by third-party services.


Functions:
    google_client_secrets(): This method will read the client secrets 
        provided by Google from the `secret/client_secret.json`
        file and return it as a dictionary object.


Author:
    Jiacheng Zhao (John)
"""
import json
import os


def google_client_secrets() -> dict:
    """This method will read the client secrets 
    provided by Google from the `secret/client_secret.json`
    file and return it as a dictionary object.
    
    
    Args:
        None.
    
    
    Returns:
        dict: The client secrets from Google.
    
    
    Raises:
        FileNotFoundError: If the file is not found. 
        json.JSONDecodeError: If the file is not a valid JSON file.
    """
    client_secret_path = os.path.join(os.path.dirname(__file__), "secret", "client_secret.json")
    with open(client_secret_path, "r") as file:
        return json.load(file)

