import os
from enum import Enum
import json
import mc
import mcserver_maker
from server_types import ServerType

serversJson = "servers.json"

# data from the servers.json file
servers = []
servers_folder = None
backups_folder = None

def initServers():
    # gets server info from json, puts it as mc.MCserver objects into servers list
    file = open(serversJson, 'r')
    data = json.load(file)
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

    global servers_folder
    servers_folder = data["servers_folder"]

    global backups_folder
    backups_folder = data["backups_folder"]

def getServerByName(name):
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

def createServer(name, server_type: ServerType, game_version: str):
    server_folder = mcserver_maker.create_server(name, servers_folder, server_type, game_version)
    if not server_folder:
        return None
    servers.append(mc.MCserver(name, server_type, server_folder, os.path.join(backups_folder, name), game_version=game_version))
    setServerInfoToJson()
    return getServerByName(name)

if __name__ == '__main__':
    initServers()
    createServer("test2", ServerType.SPIGOT, "1.20.1")
