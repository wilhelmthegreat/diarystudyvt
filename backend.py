from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, send_from_directory
import json
import requests
import os
import html
from urllib.parse import quote
from flask_cors import CORS, cross_origin
import jwt
import database.connect as database
from utils.api_response_wrapper import client_error_response
from config.jwt import jwt_algorithm, jwt_private_key, jwt_public_key
from config.flask import bind_host, flask_debug, port, flask_use_ssl, flask_key_path, flask_cert_path
from config.database import database_uri
from routes.auth import auth_routes
from routes.users import users_routes
from routes.courses import courses_routes
from routes.apps import apps_routes
from routes.entries import entries_routes
from routes.analytics import analytics_routes

dotenv_path = os.path.join(os.path.dirname(__file__), 'config', 'secret', '.env')
load_dotenv(dotenv_path)
flask_mode = os.getenv("FLASK_MODE")
if flask_mode is None:
    flask_mode = "development"
if flask_mode.lower() == "production":
    api_prefix = "/api"
else:
    api_prefix = ""

# Retrieve environment variables
MONGO_HOST = os.getenv("MONGO_HOST")
# Create the MongoDB connection string
client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
static_folder = "client"
app = Flask(__name__, static_folder=static_folder, static_url_path='')
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
# Access database and collection as usual
db = client["database"]
users = db["users"]
professors = db["professors"]

engine, Session, metadata = database.init_connection(database_uri(), echo=False)
session = Session()


app.register_blueprint(auth_routes, url_prefix=f"{api_prefix}/auth")
app.register_blueprint(users_routes, url_prefix=f"{api_prefix}/users")
app.register_blueprint(courses_routes, url_prefix=f"{api_prefix}/courses")
app.register_blueprint(apps_routes, url_prefix=f"{api_prefix}/courses/<course_id>/apps")
app.register_blueprint(entries_routes, url_prefix=f"{api_prefix}/courses/<course_id>/apps/<app_id>/entries")
app.register_blueprint(analytics_routes, url_prefix=f"{api_prefix}/courses/<course_id>/apps/<app_id>/analytics")

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api"):
        return client_error_response(
            data={},
            internal_code=-1,
            status_code=404,
            message="Resource not found",
        )
    elif flask_mode.lower() == "production":
        return app.send_static_file('index.html')
    else:
        return e


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
    if flask_use_ssl():
        app.run(
            debug=flask_debug(),
            host=bind_host(),
            port=port(),
            ssl_context=(flask_cert_path(), flask_key_path()),
        )
    else:
        app.run(debug=flask_debug(), host=bind_host(), port=port())
