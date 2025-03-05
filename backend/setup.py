import json
import os
import secrets
from pathlib import Path

from colorama import Fore, Style
from dotenv import load_dotenv, set_key

# File paths
SERVERS_JSON = Path("servers.json")
USERS_JSON = Path("users.json")
ENV_FILE = Path("backend/.env")


def create_default_servers_json():
    """Creates the default servers.json file."""
    import servers
    default_server_data = {
        "servers_folder": f"{servers.RUN_PATH_SHORTCUT}\\servers",
        "backups_folder": f"{servers.RUN_PATH_SHORTCUT}\\backups",
        "servers_list": {}
    }
    SERVERS_JSON.write_text(json.dumps(default_server_data, indent=4), encoding="utf-8")
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
    USERS_JSON.write_text(json.dumps(default_users_data, indent=4), encoding="utf-8")
    print(f"{USERS_JSON} created.")
    print(f"Username: {Fore.CYAN}admin{Style.RESET_ALL}")
    print(f"Password: {Fore.CYAN}admin123{Style.RESET_ALL}")


def create_default_env_file():
    """Creates the default .env file with a SECRET_KEY and LANG."""
    secret_key = secrets.token_hex(16)
    ENV_FILE.write_text(f'SECRET_KEY="{secret_key}"\nLANG="EN"\n', encoding="utf-8")
    print(f"{ENV_FILE} created with a generated SECRET_KEY and LANG set to 'EN'.")


def ask_for_curseforge_api_key():
    """Prompts the user for the CurseForge API key and saves it to .env."""
    cf_api_key = input(f"{Fore.CYAN}Please paste your CurseForge API Key: {Style.RESET_ALL}")
    load_dotenv()
    set_key(str(ENV_FILE), 'CURSEFORGE_API_KEY', cf_api_key)
    print("CURSEFORGE_API_KEY has been set in the .env file.")


def ensure_lang_setting():
    """Ensures a language setting exists in .env, defaults to 'EN' if missing."""
    load_dotenv()
    if not os.getenv('LANG'):
        set_key(str(ENV_FILE), 'LANG', "EN")
        print("LANG not found in .env, setting it to 'EN'.")
    else:
        print("LANG is already set.")


def verify_json_file(file_path: Path, create_default_func):
    """Checks if a JSON file exists and is valid, or creates it."""
    if not file_path.exists():
        print(f"{file_path} not found.")
        create_default_func()
    else:
        try:
            json.loads(file_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            print(f"Error decoding {file_path}, recreating it...")
            create_default_func()
        else:
            print(f"{file_path} is valid.")


def verify_env_file():
    """Checks if the .env file exists and has a valid SECRET_KEY and LANG."""
    if not ENV_FILE.exists():
        print(f"{ENV_FILE} not found.")
        create_default_env_file()
    else:
        load_dotenv()
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            secret_key = secrets.token_hex(16)
            set_key(str(ENV_FILE), 'SECRET_KEY', secret_key)
            print("Generated a new SECRET_KEY in .env file.")
        else:
            print("SECRET_KEY is valid.")

        ensure_lang_setting()

def verify_curseforge_api_key():
    """Checks if CURSEFORGE_API_KEY exists in the .env file."""
    load_dotenv()
    if not os.getenv('CURSEFORGE_API_KEY'):
        print("CURSEFORGE_API_KEY not found in the .env file.")
        ask_for_curseforge_api_key()  # Ask user to provide the key
    else:
        print("CURSEFORGE_API_KEY is valid.")


if __name__ == "__main__":
    # Verify and create all necessary files if they don't exist
    verify_env_file()  # Ensure .env exists and has a SECRET_KEY
    verify_curseforge_api_key()  # Ensure CURSEFORGE_API_KEY is set
    verify_json_file(SERVERS_JSON, create_default_servers_json)  # Check servers.json
    verify_json_file(USERS_JSON, create_default_users_json)  # Check users.json

    print(Fore.GREEN + "----SETUP COMPLETE----" + Style.RESET_ALL)

    input("Press enter to continue . . . ")
