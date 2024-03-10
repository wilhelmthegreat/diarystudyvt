"""
This module provides the blueprint for the auth routes. Right now, it is
mainly used for the third-party login functionality.


Functions:
    auth_routes: A Flask blueprint for the auth routes.
    auth_routes.google_auth(): A route to handle Google OAuth2 login.


Usage:
    This module is intended to be used as a blueprint for the auth routes in
    the main app. It should be imported and registered in the main app file.
    Example (in the backend.py file):
        from routes.auth import auth_routes
        # Below assumes you want the auth routes to be at /auth
        app.register_blueprint(auth_routes, url_prefix='/auth')


Author:
    Jiacheng Zhao (John)
"""

from flask import Blueprint, request, Response
from urllib.parse import quote
import html
import requests
import json
from config.third_party_secrets import google_client_secrets
from config.database import database_uri
import database.connect as database
from utils import jwt_utils
from utils.api_response_wrapper import (
    success_response,
    client_error_response,
    server_error_response,
)

# Set up the routes blueprint
auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/google", methods=["GET"])
def google_auth():
    """This route handles the Google OAuth2 login process."""
    # Check if the code is in the request
    if "code" not in request.args:
        return client_error_response(
            data={},
            internal_code=-102,
            status_code=400,
            message="No code provided",
        )
    # Read the code from the request
    code = request.args.get("code")
    # Sanitize the code to make it URL safe
    code = str(quote(code))
    print(code)
    # Exchange the code for an access token
    # Use the access token to access the user id
    token_url = "https://oauth2.googleapis.com/token"
    google_client_secret_dict = google_client_secrets()
    data = {
        "code": code,
        "client_id": google_client_secret_dict["web"]["client_id"],
        "client_secret": google_client_secret_dict["web"]["client_secret"],
        "redirect_uri": google_client_secret_dict["web"]["redirect_uris"][1],
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print("Response:", response.json())
        return server_error_response(
            data=response.json(),
            internal_code=-102,
            status_code=500,
            message="Failed to obtain access token",
        )
    # Access the user id
    access_token = response.json()["access_token"]
    # Santize the access token to make it URL safe
    access_token = quote(access_token)
    userinfo_url = (
        f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
    )
    response = requests.get(userinfo_url)
    print("Successfully obtained Google user Info!")
    print("User ID:", response.json()["id"])
    print("Email:", response.json()["email"])
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    # Check if the user is already registered
    user = database.get_user(session, response.json()["email"])
    if user is not None:
        user_info = {
            "isRegistered": True,
            "email": user.email,
            "jwt": jwt_utils.generate_token(
                {
                    "email": user.email,
                }
            ),
        }
        session.close()
        return success_response(user_info, internal_code=0, status_code=200, message="")
    else:
        user_info = {
            "isRegistered": False,
            "email": response.json()["email"],
            "jwt": jwt_utils.generate_token({"email": response.json()["email"]}),
        }
        session.close()
        return success_response(user_info, internal_code=0, status_code=200, message="")
    
