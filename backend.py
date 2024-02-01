from pymongo import MongoClient

# Replace 'localhost' with your VM's IP if necessary and '27017' with your MongoDB port if it's not default
client = MongoClient('mongodb://localhost:128.173.237.60/')

# Access database
mydb = client['mydatabase']
