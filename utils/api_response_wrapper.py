"""
This file contains helper methods to wrap the API response in a standard format for the client.


Functions:
    success_response(): This method will wrap the successful API response in a standard format for the client.
    client_error_response(): This method will wrap the client error API response in a standard format for the client.
    server_error_response(): This method will wrap the server error API response in a standard format for the client.


Author:
    Jiacheng Zhao (John)
"""

from flask import Response
import html
import json


def success_response(
    data: dict, internal_code: int = 0, status_code: int = 200, message: str = ""
) -> Response:
    """This method will wrap the successful API response in a standard format for the client.

    Args:
        data (dict): The data to be sent to the client.
        internal_code (int): The internal code of the response.
            In the case of a successful response, it forces to be 0.
            If not, it will raise a ValueError.
        status_code (int): The status code of the response, defaults to 200.
            If not, it will raise a ValueError.
        message (str): The message of the response.

    Raises:
        ValueError: If the internal code is not 0 or the status code is not 200.

    Returns:
        Response: The wrapped API response, ready to be sent to the client.
    """
    if status_code != 200:
        raise ValueError("The status code of a successful response must be 200.")
    if internal_code != 0:
        raise ValueError("The internal code of a successful response must be 0.")
    return Response(
        response=html.escape(
            json.dumps(
                {
                    "code": internal_code,
                    "message": message,
                    "data": data,
                }
            ),
            quote=False,
        ),
        status=status_code,
        mimetype="application/json",
    )


def client_error_response(
    data: dict, internal_code: int, status_code: int = 400, message: str = ""
) -> Response:
    """This method will wrap the client error API response in a standard format for the client.

    Args:
        data (dict): The data to be sent to the client.
        internal_code (int): The internal code of the response, it should be a negative integer.
            If not, it will raise a ValueError.
        status_code (int): The status code of the response, defaults to 400.
            If the status code is not 4XX, it will raise a ValueError.
        message (str): The message of the response.

    Raises:
        ValueError: If the status code is not 4XX.

    Returns:
        Response: The wrapped API response, ready to be sent to the client.
    """
    if status_code // 100 != 4:
        raise ValueError("The status code of a client error response must be 4XX.")
    if internal_code == 0:
        raise ValueError(
            "The internal code of a client error response must not equal to 0 "
            + "as it will be treated as a successful response in the client side."
        )
    if internal_code > 0:
        raise ValueError(
            "The internal code of a client error response must be a negative integer."
        )
    return Response(
        response=html.escape(
            json.dumps(
                {
                    "code": internal_code,
                    "message": message,
                    "data": data,
                }
            ),
            quote=False,
        ),
        status=status_code,
        mimetype="application/json",
    )


def server_error_response(
    data: dict, internal_code: int, status_code: int = 400, message: str = ""
) -> Response:
    """This method will wrap the server error API response in a standard format for the client.

    Args:
        data (dict): The data to be sent to the client.
        internal_code (int): The internal code of the response, it should be a negative integer.
            If not, it will raise a ValueError.
        status_code (int): The status code of the response, defaults to 500.
            If the status code is not 5XX, it will raise a ValueError.
        message (str): The message of the response.

    Raises:
        ValueError: If the status code is not 5XX.

    Returns:
        Response: The wrapped API response, ready to be sent to the client.
    """
    if status_code // 100 != 5:
        raise ValueError("The status code of a server error response must be 5XX.")
    if internal_code == 0:
        raise ValueError(
            "The internal code of a server error response must not equal to 0 "
            + "as it will be treated as a successful response in the client side."
        )
    if internal_code > 0:
        raise ValueError(
            "The internal code of a server error response must be a negative integer."
        )
    return Response(
        response=html.escape(
            json.dumps(
                {
                    "code": internal_code,
                    "message": message,
                    "data": data,
                }
            ),
            quote=False,
        ),
        status=status_code,
        mimetype="application/json",
    )
