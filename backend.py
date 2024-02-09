from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Retrieve environment variables

MONGO_HOST = os.getenv('MONGO_HOST')
# Create the MongoDB connection string
client = MongoClient(f'mongodb://{MONGO_HOST}:27017/')

# Access database and collection as usual
mydb = client['mydatabase']
mycollection = mydb['mycollection']

document = {"name": "Alice", "email": "alice@example.com", "age": 25}
result = mycollection.insert_one(document)
print(f"Inserted document with id {result.inserted_id}")

doc = mycollection.find_one({"name": "Alice"})
print(doc.__getattribute__)