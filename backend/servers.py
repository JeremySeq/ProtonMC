import json
import os
import shutil
from threading import Thread

import mc
import mcserver_maker
from notify import NotifyBot
from server_types import ServerType

serversJson = "servers.json"

INSTALL_PATH = str(os.getcwd())  # actual installation path


RUN_PATH_SHORTCUT = "<run_path>"  # character to represent the installation path
SERVERS_FOLDER_SHORTCUT = "<servers_folder" # character to represent the main path
# for example, if a server is in the overall servers folder, its path would just be "+\\<servername>"
BACKUPS_FOLDER_SHORTCUT = "<backups_folder>"

# data from the servers.json file
servers = []
server_creation_threads = {}

servers_folder = ""
backups_folder = ""


def full_to_short(full_path: str, run_path_only=False) -> str:
    """Converts a full path to a short path by replacing the installation path with a shortcut."""
    if not run_path_only:
        if os.path.abspath(full_path).startswith(os.path.abspath(servers_folder)):
            return SERVERS_FOLDER_SHORTCUT + os.path.abspath(full_path)[len(os.path.abspath(servers_folder)):]
        if os.path.abspath(full_path).startswith(os.path.abspath(backups_folder)):
            return BACKUPS_FOLDER_SHORTCUT + os.path.abspath(full_path)[len(os.path.abspath(backups_folder)):]
    if os.path.abspath(full_path).startswith(os.path.abspath(INSTALL_PATH)):
        return RUN_PATH_SHORTCUT + os.path.abspath(full_path)[len(os.path.abspath(INSTALL_PATH)):]
    return full_path  # Return as is if not within the installation path


def short_to_full(short_path: str) -> str:
    """Converts a short path back to a full path by replacing the shortcut with the installation path."""
    if short_path.startswith(SERVERS_FOLDER_SHORTCUT):
        return os.path.abspath(servers_folder) + short_path[len(SERVERS_FOLDER_SHORTCUT):]
    if short_path.startswith(BACKUPS_FOLDER_SHORTCUT):
        return os.path.abspath(backups_folder) + short_path[len(BACKUPS_FOLDER_SHORTCUT):]
    if short_path.startswith(RUN_PATH_SHORTCUT):
        return os.path.abspath(INSTALL_PATH) + short_path[len(RUN_PATH_SHORTCUT):]
    return short_path  # Return as is if it doesn't use the shortcut


def initServers():
    # gets server info from json, puts it as mc.MCserver objects into servers list
    file = open(serversJson, 'r')
    data = json.load(file)

    global servers_folder
    servers_folder = short_to_full(data["servers_folder"])

    global backups_folder
    backups_folder = short_to_full(data["backups_folder"])
    # create main backup folder if necessary
    try:
        os.mkdir(backups_folder)
    except FileExistsError:
        pass
    except FileNotFoundError:
        print("Could not find main backup folder.")

    server_list = data["servers_list"]
    server_info = []
    for server_name in server_list:
        server_data = server_list[server_name]
        server_type = ServerType.SPIGOT
        try:
            server_type = ServerType[server_data["server_type"]]
        except KeyError:
            pass
        server_folder = short_to_full(server_data["server_folder"])
        backup_folder = short_to_full(server_data["backup_folder"])

        game_version = None
        try:
            game_version = server_data["game_version"]
        except KeyError:
            pass

        notify_bot = None
        try:
            notify_bot_settings = server_data["notify_bot_settings"]
            notify_bot = NotifyBot(*notify_bot_settings)
        except KeyError:
            pass

        server_info.append(mc.MCserver(server_name, server_type, server_folder,
                                       backup_folder, notify_bot=notify_bot, game_version=game_version))

    global servers
    servers = server_info


def getServerByName(name) -> mc.MCserver | None:
    for server in servers:
        if server.name == name:
            return server
    return None


def setServerInfoToJson():
    servers_list = {}

    for server in servers:
        server_name = server.name
        server_folder = server.server_location
        backup_folder = server.backup_location
        server_type = server.server_type.name
        game_version = server.game_version
        notify_bot = server.notify_bot

        servers_list[server_name] = {
            "server_type": server_type,
            "server_folder": full_to_short(server_folder),
            "backup_folder": full_to_short(backup_folder),
        }

        if game_version is not None:
            servers_list[server_name]["game_version"] = game_version

        if notify_bot is not None:
            servers_list[server_name]["notify_bot_settings"] = notify_bot.get_settings()

    servers_info = {"servers_folder": full_to_short(servers_folder, run_path_only=True),
                    "backups_folder": full_to_short(backups_folder, run_path_only=True), "servers_list": servers_list}

    with open(serversJson, 'w', encoding='utf-8') as json_file:
        json.dump(servers_info, json_file, indent=4)


def asyncCreateServer(name, server_type: ServerType, game_version: str):
    def createServer(name, server_type: ServerType, game_version: str):
        server_folder = mcserver_maker.create_server(name, servers_folder, server_type, game_version)
        server_creation_threads.pop(name)
        if not server_folder:
            return None
        servers.append(mc.MCserver(name, server_type, server_folder, os.path.join(backups_folder, name),
                                   game_version=game_version))
        setServerInfoToJson()
        return getServerByName(name)

    creation_thread = Thread(target=createServer, args=(name, server_type, game_version))
    creation_thread.start()
    server_creation_threads[name] = creation_thread


def asyncDeleteServer(name):
    print(f"Deleting server {name}...")
    result = [None]

    def asyncDeleteServer():
        server = getServerByName(name)
        if server is None:
            result[0] = None
            return None
        try:
            server_creation_threads.pop(name)
        except KeyError:
            pass
        server_folder = server.server_location
        try:
            shutil.rmtree(server_folder)
        except FileNotFoundError:
            print("Could not find server folder.")
        server = getServerByName(name)
        servers.remove(server)
        try:
            if len(os.listdir(server.backup_location)) == 0:
                shutil.rmtree(server.backup_location)
                print("Deleted empty server backups folder.")
        except FileNotFoundError:
            print("Could not find server backups folder.")
        setServerInfoToJson()
        print(f"Server \"{name}\" deleted successfully.")
        result[0] = True
        return True

    thread = Thread(target=asyncDeleteServer)
    thread.start()


if __name__ == '__main__':
    initServers()
    # createServer("test2", ServerType.SPIGOT, "1.20.1")
