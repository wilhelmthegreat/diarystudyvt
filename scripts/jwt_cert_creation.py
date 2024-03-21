"""
This script will generate a new RSA key pair in the PEM format to make sure
JWT tokens are signed and verified securely. 

References:
    - https://stackoverflow.com/a/39126754
    - https://stackoverflow.com/a/22449476
"""
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import os

def jwt_create(
        export_path=os.path.join(os.path.dirname(__file__), "..", "config", "secret"),
        private_key_file_name="jwt_private.pem", 
        public_key_file_name="jwt_public.pem"
    ):
    # Check if the directory exists
    if not os.path.exists(export_path):
        print("Please make sure the directory exists.")
        exit(1)

    # Check if the public and private key files exist
    if os.path.exists(os.path.join(export_path, public_key_file_name)) or os.path.exists(os.path.join(export_path, private_key_file_name)):
        overwrite = input("The public and private key files already exist. Do you want to overwrite them? (y/n)")
        if overwrite.lower() != "y" and overwrite.lower() != "yes":
            print("Exiting...")
            exit(0)

    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )

    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write the keys to the files and set the permissions
    with open(os.path.join(export_path, private_key_file_name), "wb") as file:
        file.write(private_key)
        os.chmod(os.path.join(export_path, private_key_file_name), 0o600)

    with open(os.path.join(export_path, public_key_file_name), "wb") as file:
        file.write(public_key)
        os.chmod(os.path.join(export_path, public_key_file_name), 0o644)
    
    print("The JWT private and public keys have been successfully created.")


if __name__ == "__main__":
    jwt_create()
