import os
import sys
from dotenv import load_dotenv, set_key
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.jwt_cert_creation import jwt_create


# Define the path of the config file
SECRET_DIR = os.path.join(os.path.dirname(__file__), "..", "config", "secret")
CONFIG_FILE = os.path.join(SECRET_DIR, "config.json")
DOTENV_PATH = os.path.join(SECRET_DIR, '.env')

print()
print("Config Generator")
print("===============================")

print()

print()
print("Creating the JWT private and public keys...")
# Create the JWT private and public keys
jwt_create(export_path=SECRET_DIR)

print()
print("Setting up the necessary environment variables...")
# Load the environment variables
load_dotenv(DOTENV_PATH)

print()
print("Setting up the database URI...")

skip_database_uri = False
# Check if the database URI is set
if os.getenv("DATABASE_URI") is not None:
    print("The database URI is already set in the environment variables")
    print(f"Current database URI: {os.getenv('DATABASE_URI')}")
    overwrite = input("do you want to overwrite it? (y/n)")
    if overwrite.lower() != "y" and overwrite.lower() != "yes":
        print("Keeping the original database URI.")
        skip_database_uri = True

if not skip_database_uri:
    # Ask the user to enter the database URI
    database_uri = input("Please enter the database URI (default: sqlite:///test.sqlite): ")
    if database_uri == "":
        database_uri = "sqlite:///test.sqlite"
        # Save the database URI to the environment variables
    set_key(DOTENV_PATH, "DATABASE_URI", database_uri)
    print("The database URI has been successfully set.")

print()
print("Setting up the debug mode for the Flask app...")

skip_flask_debug = False
# Check if the debug mode for the Flask app is set
if os.getenv("FLASK_DEBUG") is not None:
    print("The debug mode for the Flask app is already set in the environment variables")
    print(f"Current debug mode: {os.getenv('FLASK_DEBUG')}")
    overwrite = input("do you want to overwrite it? (y/n)")
    if overwrite.lower() != "y" and overwrite.lower() != "yes":
        print("Keeping the original debug mode.")
        skip_flask_debug = True


if not skip_flask_debug:
    # Ask the user to enter the debug mode for the Flask app
    flask_debug = input("Please enter the debug mode for the Flask app (default: True): ")
    if flask_debug == "":
        flask_debug = "True"
    # Save the debug mode for the Flask app to the environment variables
    set_key(DOTENV_PATH, "FLASK_DEBUG", flask_debug)
    print("The debug mode for the Flask app has been successfully set.")


print()
print("Setting up the port for the Flask app...")
skip_flask_port = False
# Check if the port for the Flask app is set
if os.getenv("PORT") is not None:
    print("The port for the Flask app is already set in the environment variables")
    print(f"Current port: {os.getenv('PORT')}")
    overwrite = input("do you want to overwrite it? (y/n)")
    if overwrite.lower() != "y" and overwrite.lower() != "yes":
        print("Keeping the original port.")
        skip_flask_port = True

if not skip_flask_port:
    # Ask the user to enter the port for the Flask app
    flask_port = input("Please enter the port for the Flask app (default: 5001): ")
    if flask_port == "":
        flask_port = "5001"
    # Save the port for the Flask app to the environment variables
    set_key(DOTENV_PATH, "PORT", flask_port)
    print("The port for the Flask app has been successfully set.")


print()
print("Setting up the host for the Flask app...")
skip_flask_host = False
# Check if the host for the Flask app is set
if os.getenv("FLASK_HOST") is not None:
    print("The host for the Flask app is already set in the environment variables")
    print(f"Current host: {os.getenv('FLASK_HOST')}")
    overwrite = input("do you want to overwrite it? (y/n)")
    if overwrite.lower() != "y" and overwrite.lower() != "yes":
        print("Keeping the original host.")
        skip_flask_host = True

if not skip_flask_host:
    # Ask the user to enter the host for the Flask app
    flask_host = input("Please enter the host for the Flask app (default: 0.0.0.0): ")
    if flask_host == "":
        flask_host = "0.0.0.0"
    # Save the host for the Flask app to the environment variables
    set_key(DOTENV_PATH, "FLASK_HOST", flask_host)
    print("The host for the Flask app has been successfully set.")

print()
print("Done with setting up the environment variables!")
print("You can now run the app using the following command after activating the virtual environment and " +
      "put the Google credentials (client_secret.json) in the config/secret directory and set up the MISTRAL_API_KEY variable the .env file:")
print("python3 backend.py")
