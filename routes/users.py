from flask import Blueprint, request, Response
from urllib.parse import quote
import html
import requests
import json
from config.database import database_uri
import database.connect as database
from utils.jwt_utils import validate_token_in_request, generate_token
from utils.api_response_wrapper import (
    success_response,
    client_error_response,
    server_error_response,
)

# Set up the routes blueprint
users_routes = Blueprint("users_routes", __name__)

@users_routes.route("/", methods=["GET"])
def get_user_info():
    """This route will return the user information."""
    jwt_result = validate_token_in_request(request)
    if jwt_result["code"] != 0:
        return client_error_response(
            data={},
            internal_code=jwt_result["code"],
            status_code=401,
            message=jwt_result["message"],
        )
    payload = jwt_result["data"]
    email = payload["email"]
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is None:
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="User not found",
        )
    user_info = {
        "firstName": user.first_name,
        "lastName": user.last_name,
        "email": user.email,
        "role": user.role,
    }
    return success_response(data={"user": user_info})
    
    

@users_routes.route("/register", methods=["POST"])
def register():
    """This route will register a new user."""
    jwt_result = validate_token_in_request(request)
    if jwt_result["code"] != 0:
        return client_error_response(
            data={},
            internal_code=jwt_result["code"],
            status_code=401,
            message=jwt_result["message"],
        )
    payload = jwt_result["data"]
    data = request.get_json()
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")
    role = data.get("role")
    
    if first_name is None or last_name is None or email is None or role is None:
        return client_error_response(
            data={},
            internal_code=-401,
            status_code=400,
            message="Missing required fields",
        )
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is not None:
        return client_error_response(
            data={},
            internal_code=-402,
            status_code=409,
            message="User already exists",
        )
    if email != payload["email"]:
        return client_error_response(
            data={},
            internal_code=-403,
            status_code=401,
            message="Unauthorized",
        )
    user = database.adding_user(
        session=session,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
    )
    return success_response(
        data={
            "jwt": generate_token(
                {
                    "email": email,
                }
            )
        }
    )
    