`config/secret`
===============

This directory is used to store sensitive information which is needed by the application but should not be stored in the repository. This includes things like google API keys, database passwords, etc.

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