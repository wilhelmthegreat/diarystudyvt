from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
import json
import requests
import os
import html
from urllib.parse import quote
from flask_cors import CORS, cross_origin
import jwt
import database.connect as database
from config.jwt import jwt_algorithm, jwt_private_key, jwt_public_key
from config.flask import bind_host, flask_debug, port
from config.database import database_uri
from routes.auth import auth_routes
from routes.users import users_routes
from routes.courses import courses_routes
from routes.apps import apps_routes

dotenv_path = os.path.join(os.path.dirname(__file__), 'config', 'secret', '.env')
load_dotenv(dotenv_path)

# Retrieve environment variables
MONGO_HOST = os.getenv("MONGO_HOST")
# Create the MongoDB connection string
client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
# Access database and collection as usual
db = client["database"]
users = db["users"]
professors = db["professors"]

engine, Session, metadata = database.init_connection(database_uri(), echo=False)
session = Session()


app.register_blueprint(auth_routes, url_prefix="/auth")
app.register_blueprint(users_routes, url_prefix="/users")
app.register_blueprint(courses_routes, url_prefix="/courses")
app.register_blueprint(apps_routes, url_prefix="/courses/<course_id>/apps")

# Function to create a new course
@app.route("/professor/new_course", methods=["POST"])
def new_course():
    jwt_token = request.args.get("jwt")
    if jwt_token:
        try:
            decoded = jwt.decode(jwt_token, jwt_public_key(), algorithms=jwt_algorithm())
            email = decoded["email"]
            user = database.get_user(session, email)
            if user is not None and user.role == "professor":
                course_number = request.json["courseNumber"]
                course_name = request.json["courseName"]
                database.adding_course(session, course_name, course_number, email)
                return jsonify({"message": "Course added successfully"}), 200
        except jwt.ExpiredSignatureError:  # Error Handling
            return jsonify({"error": "Expired token"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        else:
            return jsonify({"error": "Token not found"}), 404

# Function to edit an existing course
@app.route("/professor/edit_course", methods=["PUT"])
def edit_course(course_id):
    jwt_token = request.args.get("jwt")  # Get the token from the request
    if jwt_token:
        try:
            course = database.get_course(
                course_id=course_id, session=session
            )  # Get the course from the database
            if course is not None:
                course_name = request.json[
                    "courseName"
                ]  # Get the new course name from the request
                course_number = request.json[
                    "courseNumber"
                ]  # Get the new course number from the request
                database.edit_course(session, course_id, course_name, course_number)
                return jsonify({"message": "Course updated successfully"}), 200
            else:
                return jsonify({"error": "Course not found"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Expired token"}), 401


@app.route("/professor/<username>/<course_number>/create_app", methods=["POST"])
def create_app(username, course_number):
    # TODO: Change to use SQLAlchemy instead
    # Query by professor
    professor = db.professors.find_one({"username": username})
    if professor:
        # Query by course
        course = db.courses.find_one({"course_number": course_number})
        if course:
            # Subject to change depending on frontend
            apps = course_number["apps"]
            intro = request.json["intro"]
            start_date = request.json["start_date"]
            end_date = request.json["end_date"]
            num_entries = request.json["num_entries"]
            max_students = request.json["max_students"]
            app = {
                "intro": intro,
                "start_date": start_date,
                "end_date": end_date,
                "num_entries": num_entries,
                "max_students": max_students,
            }
            apps.update_one({"course_number": course_number}, {"$set": {"apps": app}})
            return jsonify({"message": "App added successfully"}), 200
        else:
            return jsonify({"error": "Course not found"}), 404
    else:
        return jsonify({"error": "Professor not found"}), 404


@app.route("/professor/<username>/<course_number>/get_apps", methods=["GET"])
def get_apps(username, course_number):
    professor = db.professors.find_one({"username": username})
    if professor:
        course = db.courses.find_one({"course_number": course_number})
        if course:
            apps = course["apps"]
            return jsonify({"apps": apps}), 200
        else:
            return jsonify({"error": "Course not found"}), 404


@app.route("/professor/<username>/<course_number>/edit_apps", methods=["PUT"])
def edit_app(username, course_number, app_name):
    professor = db.professors.find_one({"username": username})
    if professor:
        course = db.courses.find_one(
            {"course_number": course_number}
        )  # Query by course number
        if course:
            app = course["apps"].find_one({"app_name": app_name})  # Query by app name
            if app:  # Updating attributes if app exists
                intro = request.json["intro"]
                start_date = request.json["start_date"]
                end_date = request.json["end_date"]
                num_entries = request.json["num_entries"]
                max_students = request.json["max_students"]
                app = {
                    "intro": intro,
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_entries": num_entries,
                    "max_students": max_students,
                }
                course["apps"].update_one(
                    {"app_name": app_name}, {"$set": {"apps": app}}
                )
                return jsonify({"message": "App updated successfully"}), 200
            else:
                return jsonify({"error": "App not found"}), 404


@app.route("/professor/<username>/<course_number>/get_grades", methods=["POST"])
def get_grades(username, course_number):
    # TODO: Change to use SQLAlchemy instead, and fix the query
    user = users.find_one({username: username})  # Query by username
    if user:
        course = user["courses"].find_one(
            {course_number: course_number}
        )  # Query by course number
        if course:
            return jsonify({"grades": course["grades"]}), 200
        else:
            return jsonify({"error": "Course not found"}), 404


if __name__ == "__main__":
    app.run(debug=flask_debug(), host=bind_host(), port=port())
