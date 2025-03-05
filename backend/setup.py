import json
import os
import secrets

from colorama import Fore, Style
from dotenv import load_dotenv, set_key
import servers

# File paths
SERVERS_JSON = 'servers.json'
USERS_JSON = 'users.json'
ENV_FILE = 'backend/.env'


def create_default_servers_json():
    """Creates the default servers.json file."""
    default_servers_data = {
        "servers_folder": servers.RUN_PATH_SHORTCUT + "\\servers",
        "backups_folder": servers.RUN_PATH_SHORTCUT + "\\backups",
        "servers_list": {}
    }
    with open(SERVERS_JSON, "w", encoding="utf-8") as file:
        json.dump(default_servers_data, file, indent=4)
    print(f"{SERVERS_JSON} created.")


def create_default_users_json():
    """Creates the default users.json file."""
    default_users_data = {
        "admin": {
            "username": "admin",
            "password": "admin123",
            "permissions": 5
        }
    }
    with open(USERS_JSON, "w", encoding="utf-8") as file:
        json.dump(default_users_data, file, indent=4)
    print(f"{USERS_JSON} created.")
    print("Username: " + Fore.CYAN + "admin" + Style.RESET_ALL)
    print("Password: " + Fore.CYAN + "admin123" + Style.RESET_ALL)


def create_default_env_file():
    """Creates the default .env file with a SECRET_KEY."""
    secret_key = secrets.token_hex(16)
    with open(ENV_FILE, "w", encoding="utf-8") as file:
        file.write(f"SECRET_KEY=\"{secret_key}\"\n")
    print(f"{ENV_FILE} created with a generated SECRET_KEY.")


def ask_for_curseforge_api_key():
    """Prompts the user for the CurseForge API key and saves it to .env."""
    cf_api_key = input(Fore.CYAN + "Please paste your CurseForge API Key: " + Style.RESET_ALL)

    # Save the provided key to the .env file
    load_dotenv()  # Load existing .env to set the key properly
    set_key(ENV_FILE, 'CURSEFORGE_API_KEY', cf_api_key)
    print("CURSEFORGE_API_KEY has been set in the .env file.")


def save_lang():
    load_dotenv()
    set_key(ENV_FILE, 'LANG', "EN")


def verify_json_file(file_path, create_default_func):
    """Checks if a JSON file exists and is valid, or creates it."""
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        create_default_func()
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json.load(file)  # Try loading the JSON data to verify it's valid
        except json.JSONDecodeError:
            print(f"Error decoding {file_path}, recreating it...")
            create_default_func()
        else:
            print(f"{file_path} is all good!")


def verify_env_file():
    """Checks if the .env file exists and has a valid SECRET_KEY."""
    if not os.path.exists(ENV_FILE):
        print(f"{ENV_FILE} not found.")
        create_default_env_file()
    else:
        load_dotenv()  # Load the .env file
        secret_key = os.getenv('SECRET_KEY')

        if secret_key is None:
            secret_key = secrets.token_hex(16)
            set_key(ENV_FILE, 'SECRET_KEY', secret_key)
            print("Generated a secret key in .env file.")
        else:
            print("SECRET_KEY is all good!")


def verify_curseforge_api_key():
    """Checks if CURSEFORGE_API_KEY exists in the .env file."""
    load_dotenv()
    cf_api_key = os.getenv('CURSEFORGE_API_KEY')

    if cf_api_key is None:
        print("CURSEFORGE_API_KEY not found in the .env file.")
        ask_for_curseforge_api_key()  # Ask user to provide the key
    else:
        print("CURSEFORGE_API_KEY is all good!")


if __name__ == "__main__":
    # Verify and create all necessary files if they don't exist
    verify_env_file()  # Ensure .env exists and has a SECRET_KEY
    verify_curseforge_api_key()  # Ensure CURSEFORGE_API_KEY is set
    verify_json_file(SERVERS_JSON, create_default_servers_json)  # Check servers.json
    verify_json_file(USERS_JSON, create_default_users_json)  # Check users.json

    print(Fore.GREEN + "----SETUP COMPLETE----" + Style.RESET_ALL)

    input("Press enter to continue . . . ")
