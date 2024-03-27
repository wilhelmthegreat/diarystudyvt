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

# Set up the routes blueprint
apps_routes = Blueprint("apps_routes", __name__)


@apps_routes.route("/", methods=["GET"])
@apps_routes.route("", methods=["GET"])
def get_apps(course_id: int):
    """This route will return all the apps in the given course.
    
    Args:
        course_id: The id of the course to get the apps from.
    """
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
            status_code=500,
            message="User not found",
        )
    # Check if the user is enrolled in the course
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found or user is not enrolled in the course",
        )
    apps = database.get_apps(session=session, course_id=course_id, user_email=email)
    all_apps = []
    for app in apps:
        # Get the number of students enrolled in the app
        num_students = len(app.enrolled_students)
        stopwords = []
        for stopword in app.stopwords:
            stopwords.append(stopword.word)
        all_apps.append(
            {
                "id": app.id,
                "name": app.name,
                "intro": app.intro,
                "start_time": app.start_time.timestamp(),
                "end_time": app.end_time.timestamp(),
                "num_entries": app.num_entries,
                "max_students": app.max_students,
                "num_students": num_students,
                "template_link": app.template,
                "stopwords": stopwords,
            }
        )
    session.close()
    return success_response(data={"apps": all_apps})


@apps_routes.route("/", methods=["POST"])
@apps_routes.route("", methods=["POST"])
def create_app(course_id: int):
    """This route will create a new app in the given course.
    
    Args:
        course_id: The id of the course to create the app in.
    """
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
            status_code=500,
            message="User not found",
        )
    # Check if the user is a professor
    if user.role != "professor":
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=401,
            message="User is not a professor",
        )
    # Check if the user is enrolled in the course
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found or user is not enrolled in the course",
        )
    # Create the app
    data = request.get_json()
    name = data.get("name")
    intro = data.get("intro")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    num_entries = data.get("num_entries")
    max_students = data.get("max_students")
    template_link = data.get("template_link")
    stop_words: str = data.get("stop_words")
    # Make the stop_words to be separated by a comma
    stop_words = stop_words.split(',')
    # For each stop word, remove the leading and trailing spaces
    stop_words = [word.strip() for word in stop_words]
    app = database.add_app(
        session=session,
        course_id=course_id,
        user_email=email,
        name=name,
        intro=intro,
        start_time=start_time,
        end_time=end_time,
        num_entries=num_entries,
        max_students=max_students,
        template_link=template_link,
        stopwords=stop_words
    )
    if app is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Failed to create the app",
        )
    returned_app = {
        "id": app.id,
        "name": app.name,
        "intro": app.intro,
        "start_time": app.start_time.timestamp(),
        "end_time": app.end_time.timestamp(),
        "num_entries": app.num_entries,
        "max_students": app.max_students,
        "template_link": app.template,
        "stopwords": stop_words,
    }
    session.close()
    return success_response(data={"app": returned_app})


@apps_routes.route("/<app_id>/", methods=["GET"])
@apps_routes.route("/<app_id>", methods=["GET"])
def get_app(course_id: int, app_id: int):
    """This route will return the app with the given id in the given course.
    
    Args:
        course_id: The id of the course to get the app from.
        app_id: The id of the app to get.
    """
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
            status_code=500,
            message="User not found",
        )
    # Check if the user is enrolled in the course
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found or user is not enrolled in the course",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found",
        )
    stopwords = []
    for stopword in app.stopwords:
        stopwords.append(stopword.word)
    returned_app = {
        "id": app.id,
        "name": app.name,
        "intro": app.intro,
        "start_time": app.start_time.timestamp(),
        "end_time": app.end_time.timestamp(),
        "num_entries": app.num_entries,
        "max_students": app.max_students,
        "template_link": app.template,
        "stopwords": stopwords,
    }
    session.close()
    return success_response(data={"app": returned_app})


@apps_routes.route("/<app_id>/", methods=["PUT"])
@apps_routes.route("/<app_id>", methods=["PUT"])
def edit_app(course_id: int, app_id: int):
    """This route will edit the app with the given id in the given course.
    
    Args:
        course_id: The id of the course to edit the app in.
        app_id: The id of the app to edit.
    """
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
            status_code=500,
            message="User not found",
        )
    # Check if the user is a professor
    if user.role != "professor":
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=401,
            message="User is not a professor",
        )
    # Check if the user is enrolled in the course
    course = database.get_course(session=session, course_id=course_id, user_email=email)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Course not found or user is not enrolled in the course",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found",
        )
    # Edit the app
    data = request.get_json()
    name = data.get("name")
    intro = data.get("intro")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    num_entries = data.get("num_entries")
    max_students = data.get("max_students")
    template_link = data.get("template_link")
    stop_words: str = data.get("stop_words")
    # Make the stop_words to be separated by a comma
    stop_words = stop_words.split(',')
    # For each stop word, remove the leading and trailing spaces
    stop_words = [word.strip() for word in stop_words]
    app = database.edit_app(
        session=session,
        app_id=app_id,
        user_email=email,
        name=name,
        intro=intro,
        start_time=start_time,
        end_time=end_time,
        num_entries=num_entries,
        max_students=max_students,
        template_link=template_link,
        stopwords=stop_words
    )
    if app is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Failed to edit the app",
        )
    returned_app = {
        "id": app.id,
        "name": app.name,
        "intro": app.intro,
        "start_time": app.start_time.timestamp(),
        "end_time": app.end_time.timestamp(),
        "num_entries": app.num_entries,
        "max_students": app.max_students,
        "template_link": app.template,
        "stopwords": stop_words,
    }
    session.close()
    return success_response(data={"app": returned_app})


def join_app(course_id: int, app_id: int):
    """This route will allow the user to join the app with the given id in the given course.
    
    Args:
        course_id: The id of the course to join the app in.
        app_id: The id of the app to join.
    """
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
            status_code=500,
            message="User not found",
        )
    app = database.get_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="App not found",
        )
    # Check if the user is already enrolled in the app
    if email in app.enrolled_students:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=400,
            message="User is already enrolled in the app",
        )
    # Check if the user has reached the maximum number of students
    if len(app.enrolled_students) >= app.max_students:
        session.close()
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=400,
            message="The app has reached the maximum number of students",
        )
    app = database.join_app(session=session, app_id=app_id, user_email=email)
    if app is None:
        session.close()
        return server_error_response(
            data={},
            internal_code=-1,
            status_code=500,
            message="Failed to join the app",
        )
    session.close()
    return success_response(data={})
