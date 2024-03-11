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

courses_routes = Blueprint("courses_routes", __name__)

@courses_routes.route("/", methods=["GET"])
@courses_routes.route("", methods=["GET"])
def get_courses():  
    """This route will return courses the user is enrolled in."""
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
    courses = database.get_courses(session=session, user_email=email)
    all_courses = []
    for course in courses:
        all_courses.append(
            {
                "course_number": course.identifier,
                "course_name": course.name,
                "course_id": course.id,
            }
        )
    session.close()
    return success_response(data={"courses": all_courses})


@courses_routes.route("/", methods=["POST"])
@courses_routes.route("", methods=["POST"])
def new_course():
    """This route will create a new course."""
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
    
    # Check if the user have the correct role
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
    if user.role != "professor":
        session.close()
        return client_error_response(
            data={},
            internal_code=-403,
            status_code=403,
            message="User does not have the correct role",
        )
    course_number = request.json.get("courseNumber")
    course_name = request.json.get("courseName")
    if course_number is None or course_name is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-401,
            status_code=400,
            message="Missing course number or course name",
        )
    # As course id is autoincremented, we don't need to check 
    # if the course exists. We can just add it for right now.
    # This can be changed in the future.
    database.adding_course(
        session=session,
        course_name=course_name,
        course_number=course_number,
        professor_email=email
    )
    session.close()
    return success_response(data={})


@courses_routes.route("/<course_id>", methods=["GET"])
def get_course(course_id: int):
    """This route will return the course information."""
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
    course = database.get_course(course_id=course_id, session=session)
    if course is None:
        session.close()
        return client_error_response(
            data={},
            internal_code=-402,
            status_code=404,
            message="Course not found",
        )
    session.close()
    return success_response(
        data={
            "course_number": course.identifier,
            "course_name": course.name,
            "course_id": course.id,
        }
    )
