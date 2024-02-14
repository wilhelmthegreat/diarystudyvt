from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os

load_dotenv()

# Retrieve environment variables

MONGO_HOST = os.getenv('MONGO_HOST')
# Create the MongoDB connection string
client = MongoClient(f'mongodb://{MONGO_HOST}:27017/')
app = Flask(__name__)
# Access database and collection as usual
db = client['database']
users = db['users']

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.users.find_one({'username': username})
    if user and user['password'] == password:
        # Return success message or JWT token
        return jsonify({'message': 'Student login successful'}), 200
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route("/signup", methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    new_entry = {
        'username': username,
        'password': password,
        'role': role
    }
    result = users.insert_one(new_entry)
    # Print the ID of the newly inserted document
    print('Inserted document ID:', result.inserted_id)


@app.route("/professor/<username>/courses", methods=['GET']) # Dashboard for professors
def get_courses():
    data = request.get_json() # Get the request data
    username = data.get('username') # Get the username from the request
    user = db.users.find_one({'username': username}) # Find the user in the database
    if user and user['role'] == 'professor': # Check if the user is a professor
        # Return the dashboard data such as courses and user info
        return jsonify({'courses': user['courses']}), 200
    else:
        return jsonify({'error': 'Invalid username or role'}), 404