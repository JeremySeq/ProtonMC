import json
import mc

serversJson = "servers.json"

servers = []

def getServerInfo() -> list[mc.MCserver]:
    file = open(serversJson, 'r')
    data = json.load(file)
    server_info = []
    for server_name in data:
        server_data = data[server_name]
        server_info.append(mc.MCserver(server_name, server_data["server_folder"], server_data["backup_folder"]))

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
