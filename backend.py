from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
import json
import requests
import os
import html
from urllib.parse import quote
from flask_cors import CORS, cross_origin

load_dotenv()

# Load the client secrets to access the Google API
with open('client_secret.json', 'r') as f:
    client_secrets = json.load(f)

# Retrieve environment variables
MONGO_HOST = os.getenv('MONGO_HOST')
# Create the MongoDB connection string
client = MongoClient(f'mongodb://{MONGO_HOST}:27017/')
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# Access database and collection as usual
db = client['database']
users = db['users']
professors = db['professors']

@app.route("/callback/google", methods=['GET'])
def google_callback():
    # Check if user denied access
    if 'error' in request.args:
        return Response(
            response=html.escape(
                json.dumps(
                    {
                        "code": -1, 
                        "message": "User denied access", 
                        "data": request.args
                    }
                ),
                quote=False
            ), 
            status=400,
            mimetype="application/json"
        )
    # Read the code from the request
    code = request.args['code']
    # Sanitize the code to make it URL safe
    code = quote(code)
    # Exchange the code for an access token
    # Use the access token to access the user id
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': client_secrets['web']['client_id'],
        'client_secret': client_secrets['web']['client_secret'],
        'redirect_uri': client_secrets['web']['redirect_uris'][0],
        'grant_type': 'authorization_code'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=data, headers=headers)
    # Check if the request was successful
    if response.status_code != 200:
        return Response(
            response=html.escape(
                json.dumps(
                    {
                        "code": -2, 
                        "message": "Failed to obtain access token", 
                        "data": response.json()
                    }
                ),
                quote=False
            ), 
            status=400,
            mimetype="application/json"
        )
    # Access the user id
    access_token = response.json()['access_token']
    # Santize the access token to make it URL safe
    access_token = quote(access_token)
    userinfo_url = f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}'
    response = requests.get(userinfo_url)
    print("Successfully obtained Google user Info!")
    print("User ID:", response.json()['id'])
    print("Email:", response.json()['email'])
    return Response(
        response=html.escape(
            json.dumps(
                {
                    "code": 0, 
                    "message": "Successfully obtained Google user info!", 
                    "data": response.json()
                }
            ),
            quote=False
        ), 
        status=200,
        mimetype="application/json"
    )

@cross_origin()
@app.route("/auth/google", methods=['GET'])
def google_auth():
    # Read the code from the request
    code = request.args['code']
    # Sanitize the code to make it URL safe
    code = quote(code)
    # Exchange the code for an access token
    # Use the access token to access the user id
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': client_secrets['web']['client_id'],
        'client_secret': client_secrets['web']['client_secret'],
        'redirect_uri': client_secrets['web']['redirect_uris'][1],
        'grant_type': 'authorization_code'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=data, headers=headers)
    # Check if the request was successful
    if response.status_code != 200:
        print("Response:", response.json())
        return Response(
            response=html.escape(
                json.dumps(
                    {
                        "code": -2, 
                        "message": "Failed to obtain access token", 
                        "data": response.json()
                    }
                ),
                quote=False
            ), 
            status=400,
            mimetype="application/json"
        )
    # Access the user id
    access_token = response.json()['access_token']
    # Santize the access token to make it URL safe
    access_token = quote(access_token)
    userinfo_url = f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}'
    response = requests.get(userinfo_url)
    print("Successfully obtained Google user Info!")
    print("User ID:", response.json()['id'])
    print("Email:", response.json()['email'])
    return Response(
        response=html.escape(
            json.dumps(
                {
                    "code": 0, 
                    "message": "Successfully obtained Google user info!", 
                    "data": response.json()
                }
            ),
            quote=False
        ), 
        status=200,
        mimetype="application/json"
    )

@app.route('/professor/<username>/new_course', methods=['POST'])
def new_course(username):
    professor = db.professors.find_one({'username': username})
    if professor:
        courses = professor['courses']
        course_number = request.json['course_number']
        course_name = request.json['course_name']
        credits = request.json['credits']
        course = {
            'course_number': course_number,
            'course_name': course_name,
            'credits': credits
        }
        courses.append(course)
        professors.update_one(
            {'username': username},
            {'$set': {'courses': courses}}
        )
        return jsonify({'message': 'Course added successfully'}), 200
    else:
        return jsonify({'error': 'Professor not found'}), 404

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001
    )