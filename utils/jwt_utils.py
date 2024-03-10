"""
This file contains the utility functions for JWT token generation and validation.

Functions:
    generate_token(): This method will generate a JWT token from the payload.
    validate_token(): This method will validate the JWT token and return the payload.

Author:
    Jiacheng Zhao (John)
"""
import jwt
from config.jwt import jwt_algorithm, jwt_private_key, jwt_public_key


def generate_token(payload: dict) -> str:
    """This method will generate a JWT token from the payload.

    Args:
        payload (dict): The payload to be included in the token.

    Returns:
        str: The generated JWT token.
    """
    return jwt.encode(payload, jwt_private_key(), algorithm=jwt_algorithm())


def validate_token(token: str) -> dict:
    """This method will validate the JWT token and return the payload.

    Args:
        token (str): The JWT token to be validated.

    Returns:
        dict: The payload of the token with code and message indicating if the token is valid.
            0: Valid token.
            -104: Token Expired.
            -105: Invalid Token.
            -1: Error that is not handled correctly.
    """
    try:
        payload = jwt.decode(token, jwt_public_key(), algorithms=[jwt_algorithm()])
        return {
            "code": 0,
            "message": "",
            "data": payload,
        }
    except jwt.ExpiredSignatureError:
        return {
            "code": -104,
            "message": "Token Expired",
            "data": {},
        }
    except jwt.InvalidTokenError:
        return {
            "code": -105,
            "message": "Invalid Token",
            "data": {},
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": {},
        }


def validate_token_in_request(request) -> dict:
    """This method will validate the JWT token in the request provided by
    flask and return the payload extracted from the token.

    Args:
        request (Request): The request object.

    Returns:
        dict: The payload of the token with code and message indicating if the token is valid.
            0: Valid token.
            -104: Token Expired.
            -105: Invalid Token.
            -1: Error that is not handled correctly.
    """
    token = request.args.get("jwt")
    if token is None:
        return {
            "code": -105,
            "message": "Invalid Token",
            "data": {},
        }
    return validate_token(token)
