"""Contains functions for setting up the default configs.
    - secret key in .env
    - servers.json
    - users.json
"""

import os
import json
from dotenv import load_dotenv
from servers import serversJson

def create_default_servers_json():
    file = open(serversJson, "w", encoding="utf-8")

    json.dump({
        "My Spigot Server": {
            "server_folder": "C:\\MinecraftServers\\My Spigot Server\\",
            "backup_folder": "C:\\MinecraftServers\\backups\\My Spigot Server\\"
        }
    }, file, indent=4)

    file.close()

def create_default_users_json():
    file = open("users.json", "w", encoding="utf-8")

    json.dump({
        "admin": {
            "username": "admin",
            "password": "admin123",
            "permissions": 5
        }
    }, file, indent=4)

    file.close()

def verify_servers_json():
    try:
        file = open(serversJson, 'r', encoding='utf-8')
        json.load(file)
    except FileNotFoundError:
        print("servers.json does not exist...")
        print("Creating example servers.json...")
        print("PLEASE OPEN servers.json AND FILL IN THE APPROPRIATE INFORMATION")
        create_default_servers_json()
    except json.JSONDecodeError:
        print("Error decoding servers.json")
    else:
        print("servers.json is all good!")

def verify_users_json():
    try:
        file = open("users.json", 'r', encoding='utf-8')
        json.load(file)
    except FileNotFoundError:
        print("users.json does not exist...")
        print("Creating example users.json...")
        print("PLEASE OPEN users.json AND FILL IN THE APPROPRIATE INFORMATION")
        create_default_users_json()
    except json.JSONDecodeError:
        print("Error decoding users.json")
    else:
        print("users.json is all good!")

def verify_secret_key():
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    if secret_key is None:
        print("Create a .env file with the SECRET_KEY variable")
    else:
        print("Secret key is all good!")

if __name__ == "__main__":
    verify_secret_key()
    verify_servers_json()
    verify_users_json()
