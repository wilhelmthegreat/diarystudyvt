"""
This module provides the blueprint for the apps routes.


"""
from flask import Blueprint, request, Response
from urllib.parse import quote
from config.database import database_uri
import database.connect as database
from flask_cors import CORS, cross_origin
from utils.jwt_utils import validate_token_in_request, generate_token
from utils.api_response_wrapper import (
    success_response,
    client_error_response,
    server_error_response,
)
from datetime import datetime

# Set up the routes blueprint
entries_routes = Blueprint("entries_routes", __name__)

@entries_routes.route("/", methods=["GET"])
@entries_routes.route("", methods=["GET"])
def get_entries(course_id: int, app_id: int):
    """This route will return entries the user has submitted. Or return all entries if the user is an admin."""
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
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    entries = database.get_app_entries(session=session, app_id=app_id, user_email=email)
    all_entries = []
    for entry in entries:
        all_entries.append(
            {
                "entry_id": entry.id,
                "entry_content": entry.content,
                "create_at": entry.create_at,
                "student_id": entry.student_id,
                "app_id": entry.app_id,
                "update_at": entry.update_at
            }
        )
    session.close()
    return success_response(data={"entries": all_entries})

@entries_routes.route("/", methods=["POST"])
@entries_routes.route("", methods=["POST"])
def new_entry(course_id: int, app_id: int):
    """This route will create a new entry."""
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
    content = request.json.get("content")
    if content is None:
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=400,
            message="Content is required",
        )
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the user is professor
    if user.role == "professor":
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Right now only students can submit entries, function for professors will be added later",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    # Santize the content before adding it to the database
    content = quote(content)
    # Add the entry to the database
    entry = database.add_entry(session=session, student_id=user.id, app_id=app_id, content=content)
    if entry is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Failed to add the entry",
        )
    session.close()
    return success_response(data={})


@entries_routes.route("/<entry_id>", methods=["GET"])
@entries_routes.route("/<entry_id>/", methods=["GET"])
def get_entry(course_id: int, app_id: int, entry_id: int):
    """This route will return a single entry."""
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
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    entry = database.get_entry(session=session, entry_id=entry_id, user_email=email)
    if entry is None and user.role != "professor":
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Entry not found or you are not the author of this entry",
        )
    elif user.role == "professor":
        entry = database.get_entry(session=session, entry_id=entry_id)
        if entry is None:
            session.close()
            return client_error_response(
                data={},
                internal_code=-1,
                status_code=404,
                message="Entry not found",
            )
    session.close()
    return success_response(data={"entry": entry})


@entries_routes.route("/<entry_id>", methods=["PUT"])
@entries_routes.route("/<entry_id>/", methods=["PUT"])
def update_entry(course_id: int, app_id: int, entry_id: int):
    """This route will update a single entry."""
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
    content = request.json.get("content")
    if content is None:
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=400,
            message="Content is required",
        )
    _, Session, _ = database.init_connection(database_uri(), echo=False)
    session = Session()
    user = database.get_user(session=session, email=email)
    if user is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found",
        )
    # Check if the user is professor
    if user.role == "professor":
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Right now only students can submit entries, function for professors will be added later",
        )
    # Check if the given course_id and app_id are valid
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found or you are not enrolled in this app",
        )
    entry = database.get_entry(session=session, entry_id=entry_id, user_email=email)
    if entry is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Entry not found or you are not the author of this entry",
        )
    # Santize the content before adding it to the database
    content = quote(content)
    # Update the entry in the database
    entry = database.edit_entry(session=session, entry_id=entry_id, user_email=email, entry_text=content)
    if entry is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Failed to update the entry",
        )
    session.close()
    return success_response(data={})

