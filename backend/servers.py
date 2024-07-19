import json
import mc

serversJson = "servers.json"

servers = []

def getServerInfo() -> list[mc.MCserver]:
    file = open(serversJson, 'r')
    data = json.load(file)
    servers = []
    for server_name in data:
        servers.append(mc.MCserver(*data[server_name]))

    return servers

def initServers():
    # gets server info from json, puts it as mc.MCserver objects into servers list
    global servers
    servers = getServerInfo()

def getServerByName(name):
    for server in servers:
        if server.name == name:
            return server
    return None
