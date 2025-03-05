"""
Searches for mods on Curseforge and Modrinth
Downloads mods from Curseforge and Modrinth

Search Options:
search_query: string, The query to search for
mod_loader: string, ["forge", "neoforge", "fabric"]
version: string, Minecraft version, "1.20.1"
project_type: string, ["mod", "modpack"]
"""

from enum import Enum
import os
import sys
import json
from dotenv import load_dotenv
import requests
from pick import pick

class Platform(Enum):
    """Mod platform"""
    CURSEFORGE = 1
    MODRINTH = 2

class ModType(Enum):
    """Mod Type"""
    MOD = 1
    PLUGIN = 2
    NONE = 3

class Mod():
    """Mod results from searches"""

    def __init__(self, platform: Platform, project_id, name, author, downloads, logo, link):
        self.platform = platform
        self.project_id = project_id
        self.name = name
        self.author = author
        self.downloads = downloads
        self.logo = logo
        self.link = link

    def __str__(self):
        return f"{self.name} by {self.author}"
    def __repr__(self):
        return f"{self.name} by {self.author} ({self.platform.name}:{self.project_id})"
    def to_json(self):
        """Represents mod as a json object"""
        return {
            "platform": self.platform.value,
            "project_id": self.project_id,
            "name": self.name,
            "author": self.author,
            "downloads": self.downloads,
            "logo": self.logo,
            "link": self.link
        }

load_dotenv()
curseforge_api_key = os.getenv("CURSEFORGE_API_KEY")
if curseforge_api_key is None:
    print("Add the CURSEFORGE_API_KEY variable to your .env file.")
    curseforge_api_key = ""

CURSEFORGE_API_KEY = curseforge_api_key

GAME_ID = 432
MODS_CATEGORY_ID = 6
MODPACK_CATEGORY_ID = 4471
PLUGINS_CATEGORY_ID = 5

def search_modrinth_mods(search_query, mod_loader=None, version=None, project_type=ModType.MOD, limit=40):
    """Searches Modrinth for mods"""

    url = 'https://api.modrinth.com/v2/search'

    facets = []
    if version:
        facets.append([f'versions:{version}'])
    if mod_loader:
        facets.append([f'categories:{mod_loader}'])
    if project_type:
        if project_type == ModType.MOD:
            project_type = "mod"
        elif project_type == ModType.PLUGIN:
            project_type = "plugin"
        facets.append([f'project_type:{project_type}'])
    facets = json.dumps(facets)

    params = {
        'query': search_query,
        'limit': limit,
        "facets": facets
    }

    response = requests.get(url, params=params, timeout=4)

    if response.status_code != 200:
        return response.status_code

    response = response.json()

    search_results = []
    mods = response["hits"]
    for mod_result in mods:
        project_id = mod_result["project_id"]
        name = mod_result["title"]
        author = mod_result["author"]
        downloads = mod_result["downloads"]
        logo = mod_result["icon_url"]
        link = f"https://modrinth.com/{project_type}/{mod_result['slug']}"

        search_results.append(Mod(Platform.MODRINTH, project_id, name, author, downloads, logo, link))

    return search_results

def search_curseforge_mods(search_query, mod_loader=None, version=None, project_type=ModType.MOD, limit=40):
    """Searches Curseforge for mods"""

    headers = {
        'Accept': 'application/json',
        'x-api-key': CURSEFORGE_API_KEY
    }

    params = {
        'gameId': GAME_ID,
        'sortField': 2,
        'sortOrder': "desc",
        "searchFilter": search_query,
        "pageSize": limit
    }

    if mod_loader:
        if mod_loader == "forge":
            params["modLoaderType"] = 1
        elif mod_loader == "neoforge":
            params["modLoaderType"] = 6
        elif mod_loader == "fabric":
            params["modLoaderType"] = 4
    if version:
        params["gameVersion"] = version
    if project_type:
        if project_type == ModType.MOD:
            params["classId"] = MODS_CATEGORY_ID
        # elif project_type == "modpack":
        #     params["classId"] = MODPACK_CATEGORY_ID
        elif project_type == ModType.PLUGIN:
            params["classId"] = PLUGINS_CATEGORY_ID

    url = 'https://api.curseforge.com/v1/mods/search'
    response = requests.get(url, params=params, headers = headers, timeout=4)

    if response.status_code != 200:
        return response.status_code

    response = response.json()

    search_results = []
    mods = response["data"]
    for mod_result in mods:
        project_id = mod_result["id"]
        name = mod_result["name"]
        author = mod_result["authors"][0]["name"]
        downloads = mod_result["downloadCount"]
        link = mod_result["links"]["websiteUrl"]
        try:
            logo = mod_result["logo"]["url"]
        except TypeError:
            logo = None

        search_results.append(Mod(Platform.CURSEFORGE, project_id, name, author, downloads, logo, link))

    return search_results

def download_curseforge_plugin(project_id, destination_path):
    """
    Downloads a plugin from curseforge given its project id
    to a destination path.
    Returns [message, status_code]
    """
    headers = {
        'Accept': 'application/json',
        'x-api-key': CURSEFORGE_API_KEY
    }

    params = {
    }

    url = f'https://api.curseforge.com/v1/mods/{project_id}/files'

    try:
        r = requests.get(url, headers = headers, params=params, timeout=4)
    except requests.exceptions.ReadTimeout:
        return "Could not connect to Curseforge.", 500

    if r.status_code != 200:
        print("Request to " + url + " failed with status code " + str(r.status_code))
        return "Could not connect to Curseforge.", 500

    files_found = r.json()["data"]

    if len(files_found) > 0:
        # download the first file
        filename = files_found[0]["fileName"]
        download_url = files_found[0]["downloadUrl"]
        response = requests.get(download_url, timeout=4)
        if response.status_code == 200:
            with open(os.path.join(destination_path, filename), 'wb') as file:
                file.write(response.content)
                print(f"Downloaded {filename}")
            return "Downloaded plugin.", 200
        else:
            print(f"Failed to download {filename}")
            return "Download failed.", 500
    else:
        return "No compatible files found.", 500

def download_curseforge_mod(project_id, destination_path, mod_loader, minecraft_version):
    """Downloads a mod from Curseforge given its project id 
    (+ modloader and minecraft version) to a destination path.
    Returns [message, status_code]"""
    headers = {
        'Accept': 'application/json',
        'x-api-key': CURSEFORGE_API_KEY
    }

    def get_curseforge_modloader_enum(mod_loader: str):
        if mod_loader == "forge":
            return 1
        elif mod_loader == "neoforge":
            return 6
        elif mod_loader == "fabric":
            return 4

    params = {
        "gameVersion": minecraft_version,
        "modLoaderType": get_curseforge_modloader_enum(mod_loader)
    }


    url = f'https://api.curseforge.com/v1/mods/{project_id}/files'
    try:
        r = requests.get(url, headers = headers, params=params, timeout=4)
    except requests.exceptions.ReadTimeout:
        return "Could not connect to Curseforge.", 500

    if r.status_code != 200:
        print("Request to " + url + " failed with status code " + str(r.status_code))
        return "Could not connect to Curseforge.", 500

    files_found = r.json()["data"]

    if len(files_found) > 0:
        # download the first file
        filename = files_found[0]["fileName"]
        download_url = files_found[0]["downloadUrl"]
        response = requests.get(download_url, timeout=4)
        if response.status_code == 200:
            with open(os.path.join(destination_path, filename), 'wb') as file:
                file.write(response.content)
                print(f"Downloaded {filename}")
            return "Downloaded mod.", 200
        else:
            print(f"Failed to download {filename}")
            return "Download failed.", 500
    else:
        return "No compatible files found.", 500

def download_modrinth_plugin(project_id, destination_path):
    """
    Downloads a plugin from Modrinth given its project id
    to a destination path.

    Return [message, status_code]
    """
    url = f'https://api.modrinth.com/v2/project/{project_id}/version'

    params = {
        "loaders": f'["bukkit"]',
    }

    try:
        r = requests.get(url, params=params, timeout=4)
    except requests.exceptions.ReadTimeout:
        return "Could not connect to Modrinth.", 500

    if r.status_code != 200:
        print("Request to " + url + " failed with status code " + str(r.status_code))
        return "Could not connect to Modrinth.", 500

    files_found = r.json()

    if len(files_found) > 0:
        # download the first file
        file = files_found[0]["files"][0]
        filename = file["filename"]
        download_url = file["url"]
        r = requests.get(download_url, timeout=4)
        if r.status_code == 200:
            with open(os.path.join(destination_path, filename), 'wb') as file:
                file.write(r.content)
                print(f"Downloaded {filename}")
            return "Downloaded plugin.", 200
        else:
            print(f"Failed to download {filename}")
            return "Download failed.", 500
    else:
        return "No compatible files found.", 500


def download_modrinth_mod(project_id, destination_path, mod_loader, minecraft_version):
    """Downloads a mod from Modrinth given its project id 
    (+ modloader and minecraft version) to a destination path.
    Returns [message, status_code]"""

    url = f'https://api.modrinth.com/v2/project/{project_id}/version'


    params = {
        "loaders": f'["{mod_loader}"]',
        "game_versions": f'["{minecraft_version}"]'
    }
    try:
        r = requests.get(url, params=params, timeout=4)
    except requests.exceptions.ReadTimeout:
        return "Could not connect to Modrinth.", 500

    if r.status_code != 200:
        print("Request to " + url + " failed with status code " + str(r.status_code))
        return "Could not connect to Modrinth.", 500

    files_found = r.json()

    if len(files_found) > 0:
        # download the first file
        file = files_found[0]["files"][0]
        filename = file["filename"]
        download_url = file["url"]
        r = requests.get(download_url, timeout=4)
        if r.status_code == 200:
            with open(os.path.join(destination_path, filename), 'wb') as file:
                file.write(r.content)
                print(f"Downloaded {filename}")
            return "Downloaded mod.", 200
        else:
            print(f"Failed to download {filename}")
            return "Download failed.", 500
    else:
        return "No compatible files found.", 500

if __name__ == "__main__":
    # r = search_curseforge_mods("dungeons", mod_loader="forge", version="1.20.1")
    # r = search_modrinth_mods("dungeons weaponry", mod_loader="forge", version="1.20.1")

    # if isinstance(r, list):
    #     for mod in r:
    #         print(mod, mod.project_id)
    # else:
    #     print("Error: " + str(r))

    SERVER_FOLDER = "J:\\MinecraftServers\\Test"

    title = 'Website: '
    options = ["Curseforge", "Modrinth"]
    selected_platform, index = pick(options, title)
    selected_platform = Platform.CURSEFORGE if index == 0 else Platform.MODRINTH
    print(selected_platform.name)

    title = 'Modloader: '
    options = ["forge", "neoforge", "fabric"]
    mod_loader, index = pick(options, title)
    print(f"Modloader: {mod_loader}")

    version = input("Version: ")

    query = input("Search query: ")
    if selected_platform == Platform.CURSEFORGE:
        mods = search_curseforge_mods(query, mod_loader=mod_loader, version=version)
    else:
        mods = search_modrinth_mods(query, mod_loader=mod_loader, version=version)
    if len(mods) == 0:
        print("No mods found")
    else:
        title = 'Choose a mod to download: '
        options = [f"{mod.name} by {mod.author}" for mod in mods]
        option, index = pick(options, title)
        print(option)
        selected_mod = mods[index]
        if selected_platform == Platform.CURSEFORGE:
            print(download_curseforge_mod(selected_mod.project_id, os.path.join(SERVER_FOLDER, "mods"), mod_loader, version))
        else:
            print(download_modrinth_mod(selected_mod.project_id, os.path.join(SERVER_FOLDER, "mods"), mod_loader, version))

    # print(download_curseforge_mod("538567", os.path.join(SERVER_FOLDER, "mods"), "forge", "1.20.1"))
    # print(download_modrinth_mod("NrWDtgVf", os.path.join(SERVER_FOLDER, "mods"), "forge", "1.20.1"))
