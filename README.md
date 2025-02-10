# DiaryQuest - Backend

This serves as the backend for the DiaryQuest project.

## Menu

- [Prerequisites](#prerequisites)
- [Setup](#setup)
    - [Obtain the code](#obtain-the-code)
    - [Setup environment](#setup-environment)
        - [Create a virtual environment](#create-a-virtual-environment)
        - [Use the virtual environment](#use-the-virtual-environment)
        - [Install dependencies](#install-dependencies)
        - [Setup the configuration](#setup-the-configuration)
- [Running the server](#running-the-server)

## Prerequisites

> To run the script smoothly, make sure you have the following installed in your system:

- [Python 3.10](https://www.python.org/downloads/) (please not try to run the script with 3.11 or above as it may not work for some dependencies)
- [PyPi](https://packaging.python.org/en/latest/tutorials/installing-packages/) (Python package installer)
- [Virtual Environment of Python](https://virtualenv.pypa.io/en/latest/installation.html#via-pip)

## Set Up

### Obtain the code

You can get the source code by cloning the repository:

> [!NOTE]
> The code below assumes that you are in the directory where you want to store the project. 
> If you are in the frontend directory, please change to the parent directory before running the command.

```bash
git clone git@github.com:McCrickard-Lab/Diary-Study-Back-End.git DiaryQuest-Backend # This will clone the repository to a folder named DiaryQuest-Backend

cd DiaryQuest-Backend
```

[Back to top](#menu)

### Setup environment

#### Create a virtual environment

* Windows PowerShell:

    ```powershell
    python -m virtualenv .venv
    .\.venv\Scripts\activate.ps1 # This will activate the virtual environment
    ```

* macOS/Linux Shell:

    ```bash
    python3 -m virtualenv .venv
    . .venv/bin/activate # This will activate the virtual environment
    ```

[Back to top](#menu)

#### Use the virtual environment

> [!NOTE]
> You need to activate the virtual environment every time you open a new terminal. This makes sure that it would not interfere with the system's Python global packages, and it will use the packages installed in the virtual environment.

* Windows PowerShell:

    ```powershell
    .\.venv\Scripts\activate.ps1
    ```

* macOS/Linux Shell:

    ```bash
    . .venv/bin/activate
    ```

[Back to top](#menu)

#### Install dependencies

* Windows PowerShell:

    ```powershell
    pip install -r requirements.txt
    ```

* macOS/Linux:

    ```bash
    pip3 install -r requirements.txt
    ```

[Back to top](#menu)

#### Setup the configuration

Run the following command to setting up necessary environment variables for the backend (for details on the environment variables needed, you may refer to [README.md](config/secret/README.md) file in the `config/secret` directory):

> [!NOTE]
> As the backend utilizes the [Object Relational Mapping (ORM)](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping), you need to specify the database URI to connect to the database. If you are not sure about setting up, you may refer to the [SQLAlchemy documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) on how to set up the database URI for the database you are using.

> [!IMPORTANT]
> This settings may not include all the necessary environment variables. Please refer to the [README.md](config/secret/README.md) file in the `config/secret` directory for the complete list of environment variables needed.

* Windows PowerShell:

    ```powershell
    python scripts\config_generator.py
    ```

* macOS/Linux:

    ```bash
    python3 scripts/config_generator.py
    ```

[Back to top](#menu)

## Running the server

To start the backend server, run the following command:

> [!NOTE]
> Make sure you are in the backend directory before running the command.

* Windows PowerShell:

  ```powershell
  .\.venv\Scripts\activate.ps1
  python backend.py
  ```

* macOS/Linux:

  ```bash
  . .venv/bin/activate
  python3 backend.py
  ```

The server will start running on the port specified in the [`.env`](config/secret/.env) file.

[Back to top](#menu)
