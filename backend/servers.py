import os
from enum import Enum
import json
from threading import Thread
import shutil
import mc
import mcserver_maker
from server_types import ServerType

serversJson = "servers.json"

# data from the servers.json file
servers = []
server_creation_threads = {}

servers_folder = None
backups_folder = None

def initServers():
    # gets server info from json, puts it as mc.MCserver objects into servers list
    file = open(serversJson, 'r')
    data = json.load(file)

    global servers_folder
    servers_folder = data["servers_folder"]

    global backups_folder
    backups_folder = data["backups_folder"]
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
        server_folder = server_data["server_folder"]
        backup_folder = server_data["backup_folder"]

        game_version = None
        try:
            game_version = server_data["game_version"]
        except KeyError:
            pass
        server_info.append(mc.MCserver(server_name, server_type, server_folder,
                                       backup_folder, game_version=game_version))

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

        if game_version is not None:
            servers_list[server_name] = {
                "server_type": server_type,
                "server_folder": server_folder,
                "backup_folder": backup_folder,
                "game_version": game_version
            }
        else:
            servers_list[server_name] = {
                "server_type": server_type,
                "server_folder": server_folder,
                "backup_folder": backup_folder,
            }

    server_info = {"servers_folder": servers_folder, "backups_folder": backups_folder,"servers_list": servers_list}        

    with open(serversJson, 'w', encoding='utf-8') as json_file:
        json.dump(server_info, json_file, indent=4)

def asyncCreateServer(name, server_type: ServerType, game_version: str):
    def createServer(name, server_type: ServerType, game_version: str):
        server_folder = mcserver_maker.create_server(name, servers_folder, server_type, game_version)
        server_creation_threads.pop(name)
        if not server_folder:
            return None
        servers.append(mc.MCserver(name, server_type, server_folder, os.path.join(backups_folder, name), game_version=game_version))
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
