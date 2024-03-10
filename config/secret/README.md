`config/secret`
===============

This directory is used to store sensitive information which is needed by the application but should not be stored in the repository. This includes things like google API keys, database passwords, etc.

> [!CAUTION]
> Do not commit any files in this directory to the repository except for the `README.md` file. All other files in this directory have been added to the `.gitignore` file and should not be committed to the repository.

File Structure
--------------

```
config/secret/
├── README.md   # The instructions which you are reading now
├── client_secret.json  # Google API client secrets
├── jwt_private.pem  # The private key used to sign JWTs
├── jwt_public.pem  # The public key used to verify JWTs
└── .env    # The environment variables used by the application
```

Detailed Description
--------------------

- `client_secret.json`: This file contains the client secrets for the google API. Contact the project maintainer to get this file.
- `jwt_private.pem` and `jwt_public.pem`: These files contain the private and public keys used to sign and verify JWTs. You can generate these keys by running the [`jwt_cert_creation.py`](../../scripts/jwt_cert_creation.py) script.
- `.env`: This file contains the environment variables used by the application. Right now, you should have the following environment variables in this file:
  - `MONGO_HOST`: The host of the MongoDB server (this will be replaced by the `DATABASE_URI` after the overall refactor is complete, keeping it here for now for backwards compatibility with the old codebase)
  - `DATABASE_URI`: The URI of the database server (including the username and password)
  - `FLASK_DEBUG`: Set this to `True` to enable debug mode in Flask
  - `PORT`: The port on which the application should run
  - `FLASK_HOST`: The binding host for the Flask application