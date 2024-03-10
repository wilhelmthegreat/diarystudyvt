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
import jwt

# Set up the routes blueprint
auth_routes = Blueprint('auth_routes', __name__)


@auth_routes.route('/google', methods=["GET"])
def google_auth():
    """This route handles the Google OAuth2 login process.
    """
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
        return Response(
            response=html.escape(
                json.dumps(
                    {
                        "code": -102,
                        "message": "Failed to obtain access token",
                        "data": response.json(),
                    }
                ),
                quote=False,
            ),
            status=400,
            mimetype="application/json",
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
    engine, Session, metadata = database.init_connection(database_uri(), echo=False)
    session = Session()
    # Check if the user is already registered
    user = database.get_user(session, response.json()["email"])
    if user is not None:
        user_info = {
            "isRegistered": True,
            "email": user.email,
            "jwt": jwt.encode(
                {
                    "email": user.email,
                },
                "secret",
            ),
        }
        return Response(
            response=html.escape(
                json.dumps({"code": 0, "message": "", "data": user_info}), quote=False
            ),
            status=200,
            mimetype="application/json",
        )
    else:
        user_info = {
            "isRegistered": False,
            "email": response.json()["email"],
            "jwt": jwt.encode({"email": response.json()["email"]}, "secret"),
        }
        return Response(
            response=html.escape(
                json.dumps({"code": 0, "message": "", "data": user_info}), quote=False
            ),
            status=200,
            mimetype="application/json",
        )

