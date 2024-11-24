import zipfile
import os
import json
import toml
import mod_helper
import difflib


def extract_mod_metadata(jar_path):
    metadata_files = ['mcmod.info', 'fabric.mod.json', 'META-INF/mods.toml']
    
    with zipfile.ZipFile(jar_path, 'r') as jar:
        for file in metadata_files:
            if file in jar.namelist():
                with jar.open(file) as meta_file:
                    return [file, meta_file.read()]
    return None

def read_fabric_json(data):
    parsed_json = json.loads(data)
    display_name = parsed_json['name']
    authors = ""
    if len(parsed_json['authors']) > 0:
        try:
            authors = [author["name"] for author in parsed_json['authors']]
        except TypeError:
            authors = parsed_json['authors']

    return display_name, ', '.join(authors)

def read_forge_toml(data):
    parsed_toml = toml.loads(data)
    display_name = parsed_toml["mods"][0]["displayName"]
    authors = ""
    try:
        authors = parsed_toml["mods"][0]["authors"]
    except KeyError:
        pass
    return display_name, authors

def match(display_name, authors):
    mods = mod_helper.search_curseforge_mods(display_name, limit=50)
    mod_strings = [mod.name for mod in mods]

    matches = difflib.get_close_matches(display_name, mod_strings, n=1, cutoff=0.0)

    bestMatch = None
    for match in matches:

        match_mod = None
        for x in mods:
            if x.name == match:
                match_mod = x
        if match_mod is None:
            continue

        if match_mod.author in authors:
            bestMatch = match_mod
            break

    if bestMatch is None:
        match_mod = None
        for x in mods:
            if x.name == matches[0]:
                match_mod = x
        bestMatch = match_mod

    return bestMatch

def get_mod_name(filepath):
    """Extracts mod name from jar file by looking for mod metadata files."""
    name = os.path.split(filepath)[1]
    metadata = extract_mod_metadata(filepath)
    if metadata is None:
        return name
    file_read = os.path.split(metadata[0])[1]
    if file_read == "mods.toml":
        data = metadata[1].decode('utf-8')
        name = read_forge_toml(data)[0]
        return name
    elif file_read == 'fabric.mod.json':
        data = metadata[1].decode('utf-8')
        name = read_fabric_json(data)[0]
    return name

if __name__ == '__main__':
    SERVER_FOLDER = "J:\\MinecraftServers\\Test\\mods\\dungeonsweaponry-1.16.2-1.20.1.jar"
    SERVER_FOLDER = "J:\\MinecraftServers\\Test\\"

    mods_folder = os.path.join(SERVER_FOLDER, "mods")

    for dirpath, dirnames, filenames in os.walk(mods_folder):
        for file in filenames:
            path = os.path.join(dirpath, *dirnames, file)
            metadata = extract_mod_metadata(path)
            file_read = os.path.split(metadata[0])[1]

            if file_read == "mods.toml":
                data = metadata[1].decode('utf-8')
                bestMatch = match(*read_forge_toml(data))
                print(f"{file} => {bestMatch}")
            elif file_read == 'fabric.mod.json':
                data = metadata[1].decode('utf-8')
                bestMatch = match(*read_fabric_json(data))
                print(f"{file} => {bestMatch}")
            with open(file_read, 'wb') as file:
                file.write(metadata[1])
