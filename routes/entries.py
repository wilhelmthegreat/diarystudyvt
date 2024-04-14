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
import modelling

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

def get_entries_dashboard(course_id:int, app_id: int):
    """This route will get the wordcloud object of all entries in a coures if the user is a professor"""
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
    if user is None or user.role != "professor":
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found or User is not a professor",
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
    entries = database.get_app_entries(session=session, app_id=app_id)
    all_entries = []
    sents = []
    for entry in entries:
        all_entries.append(entry.content)
        sents.append({
            'sentence': modelling.get_sentence_no_word(entry.content),
            'sentiment': modelling.sentiment(entry.content),
            'user': entry.student_id
            })
    stopw = []
    for stopword in app.stopwords:
        stopw.apend(stopword.word)
    session.close()
    return success_response(data={
        "wordcloud": modelling.word_cloud('\n'.join(all_entries), stopw, 12),
        "sentences": sents,
        "graph": {'x': [modelling.word_count(e) for e in all_entries], 'y': [modelling.sentiment(e) for e in all_entries]}
        })

def word_clicked_dashboard(course_id:int, app_id:int, wrd:str):
    """This route will get the wordcloud object of all entries in a coures if the user is a professor"""
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
    if user is None or user.role != "professor":
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="User not found or User is not a professor",
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
    entries = database.get_app_entries(session=session, app_id=app_id)
    all_entries = []
    sents = []
    for entry in entries:
        all_entries.append(entry.content)
        sents.append({
            'sentence': modelling.get_sentence(entry.content, wrd),
            'sentiment': modelling.sentiment(entry.content),
            'user': entry.student_id
            })
    stopw = []
    for stopword in app.stopwords:
        stopw.append(stopword.word)
    session.close()
    return success_response(data={
        'wordcloud': modelling.associated_word_cloud('\n'.join(all_entries), wrd),
        'sentences': sents
    })

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
    entry_text = request.json.get("entry_text")
    study_start_time = request.json.get("study_start_time")
    study_duration_minutes = request.json.get("study_duration_minutes")
    if entry_text is None:
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
    # Check if the user joined the app
    if not database.check_user_in_app(session=session, app_id=app_id, user_email=email):
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=403,
            message="You are not enrolled in this app",
        )
    # Santize the content before adding it to the database
    entry_text = quote(entry_text)
    # Add the entry to the database
    entry = database.add_entry(session=session, student_email=email, app_id=app_id, entry_text=entry_text, study_start_time=study_start_time, study_duration_minutes=study_duration_minutes)
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
    study_start_time = request.json.get("study_start_time")
    study_duration_minutes = request.json.get("study_duration_minutes")
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
    entry = database.edit_entry(session=session, entry_id=entry_id, user_email=email, entry_text=content, study_start_time=study_start_time, study_duration_minutes=study_duration_minutes)
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

