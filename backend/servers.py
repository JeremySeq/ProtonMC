import os
from enum import Enum
import json
import mc
import mcserver_maker
from server_types import ServerType

serversJson = "servers.json"

servers = []

def getServerInfo() -> list[mc.MCserver]:
    file = open(serversJson, 'r')
    data = json.load(file)
    server_info = []
    for server_name in data:
        server_data = data[server_name]
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
    return server_info

def initServers():
    # gets server info from json, puts it as mc.MCserver objects into servers list
    global servers
    servers = getServerInfo()
def getServerByName(name):
    for server in servers:
        if server.name == name:
            return server
    return None

def setServerInfoToJson():
    server_info = {}

    for server in servers:
        server_name = server.name
        server_folder = server.server_location
        backup_folder = server.backup_location
        server_type = server.server_type.name
        server_info[server_name] = {
            "server_type": server_type,
            "server_folder": server_folder,
            "backup_folder": backup_folder
        }

    with open(serversJson, 'w', encoding='utf-8') as json_file:
        json.dump(server_info, json_file, indent=4)

def createServer(name):
    server_folder = mcserver_maker.create_spigot_server(name)
    if not server_folder:
        return None
    servers.append(mc.MCserver(name, ServerType.SPIGOT, server_folder, os.path.join(os.getcwd(), f"backups\\{name}")))
    setServerInfoToJson()
    return getServerByName(name)

if __name__ == '__main__':
    initServers()
    createServer("test")
