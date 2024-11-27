"""Contains routes for controlling Minecraft servers"""
import os
from flask import Blueprint, request, jsonify, send_from_directory
import servers
from server_types import ServerType
from loginRoutes import token_required, requiresUserPermissionLevel
import mod_helper
from permissions import permissions
import mcserver_maker
from mc import MCserver

server_routes = Blueprint('backups', __name__)

def check_server_exists(func):
    """Decorator for routes that checks if the server name 
    given as the first argument is an existing server.
    """
    def inner1(*args, **kwargs):
        server = servers.getServerByName(kwargs["server"])
        if server is None:
            return jsonify({"message": "Server does not exist"}), 404
        returned_value = func(*args, **kwargs)
        return returned_value
    inner1.__name__ = func.__name__
    return inner1

@server_routes.route('/')
@token_required
def get_servers():
    """Returns list of servers and their statuses"""
    s = [{"name": server.name, "status": server.getServerStatus().value} for server in servers.servers]
    for server_creating in servers.server_creation_threads.keys():
        s.append({"name": server_creating, "status": MCserver.ServerStatus.CREATING.value})
    return jsonify(s), 200

@server_routes.route('/', methods=["POST"])
@token_required
@requiresUserPermissionLevel(permissions["create_server"])
def create_server():
    """Creates a new server."""
    new_server_name = request.form.get("name")
    new_server_type = request.form.get("type") if request.form.get("type") else "spigot"
    new_server_version = request.form.get("version")

    try:
        new_server_type = ServerType[new_server_type.upper()]
    except KeyError:
        return jsonify({"message": "Invalid server type."}, 400)

    print(f"Creating new server \"{new_server_name}\" with type {new_server_type.name}")

    servers.asyncCreateServer(new_server_name, new_server_type, new_server_version)
    return jsonify({"message": "Creating server..."}), 200

@server_routes.route('/', methods=["DELETE"])
@token_required
@requiresUserPermissionLevel(permissions["create_server"])
def delete_server():
    """Deletes a server"""
    server_name = request.form.get("name")
    server = servers.getServerByName(server_name)
    if server is None:
        return jsonify({"message": "Server does not exist"}), 404
    servers.asyncDeleteServer(server_name)
    return jsonify({"message": "Deleting server..."}), 200

# TODO: move all the create server stuff to a different api route (not the server_routes)
# or better yet, make server names not able to use underscores.
@server_routes.route('/game_versions', methods=["GET"])
@token_required
@requiresUserPermissionLevel(permissions["create_server"])
def get_available_game_versions():
    """
    Returns a list of available game versions for a specified server type.
    """

    new_server_type = request.args.get("type") if request.args.get("type") else "spigot"
    try:
        new_server_type = ServerType[new_server_type.upper()]
    except KeyError:
        return jsonify({"message": "Invalid server type."}, 200)

    versions = mcserver_maker.get_versions_available(new_server_type)
    return jsonify({"message": versions}), 200

@server_routes.route('/<server>', methods=["GET"])
@token_required
@check_server_exists
def get_server(server):
    """
    Returns server info: name, type, game version
    """
    server = servers.getServerByName(server)
    return jsonify({"name": server.name, "type": server.server_type.name, "game_version": server.game_version})

@server_routes.route('/<server>/status', methods=["GET"])
@token_required
@check_server_exists
def get_server_status(server):
    """Returns server status [isRunning, isOperational].
    isRunning is True if the server thread is running.
    isOperational is True if the server has finished starting up and players can join the server.
    """
    server = servers.getServerByName(server)
    return jsonify({"message": [server.isServerRunning(), server.isServerOperational()]}), 200

@server_routes.route('/<server>/status/players')
@token_required
@check_server_exists
def get_server_players(server):
    """Returns the players currently on the server"""
    server = servers.getServerByName(server)
    return jsonify({"players": server.players}), 200

@server_routes.route('/<server>/uptime', methods=["GET"])
@token_required
@check_server_exists
def get_uptime(server):
    """Returns uptime as a string in format: hh:mm:ss"""
    server = servers.getServerByName(server)
    uptime = server.getUptime()
    return jsonify({"message": uptime}), 200


@server_routes.route('/<server>/status/startTime', methods=["GET"])
@token_required
@check_server_exists
def get_start_time(server):
    """Returns the time in seconds since the epoch when the server started. """
    server = servers.getServerByName(server)
    start_time = server.getStartTime()
    return jsonify({"message": start_time}), 200

@server_routes.route('/<server>/start', methods=["POST"])
@token_required
@check_server_exists
def start_server(server):
    """"Starts the server if it is not running. """
    server = servers.getServerByName(server)
    if not server.isServerRunning():
        server.startServerThread()
        return jsonify({"message": True}), 200
    return jsonify({"message": False}), 200

@server_routes.route('/<server>/stop', methods=["POST"])
@token_required
@check_server_exists
def stop_server(server):
    """Stops the server if it is running."""
    server = servers.getServerByName(server)
    if server.isServerRunning():
        server.stop()
        return jsonify({"message": True}), 200
    return jsonify({"message": False}), 200

@server_routes.route('/<server>/console', methods=["GET"])
@token_required
@requiresUserPermissionLevel(permissions["view_console"])
@check_server_exists
def get_console(server):
    """Returns console lines"""
    server = servers.getServerByName(server)

    return jsonify(server.console), 200

@server_routes.route('/<server>/console', methods=["POST"])
@token_required
@requiresUserPermissionLevel(permissions["send_command"])
@check_server_exists
def send_command(server):
    """Sends a console command"""
    server = servers.getServerByName(server)
    command = server.runCommand(request.form.get("command"))
    return jsonify({"message": command}), 200

@server_routes.route('/<server>/backup', methods=["GET"])
@token_required
@check_server_exists
def get_backups(server):
    """Returns backup list"""
    server = servers.getServerByName(server)

    return jsonify(server.getBackups()), 200

@server_routes.route('/<server>/backup', methods=["POST"])
@token_required
@requiresUserPermissionLevel(permissions["create_backup"])
@check_server_exists
def create_backup(server):
    """Creates a backup."""
    server = servers.getServerByName(server)
    if server.getBackupProgress()[0]:
        return jsonify({"message": "A backup for this server is already in progress."}), 200
    server.startBackup()
    return jsonify({"message": "Backup started."}), 200

@server_routes.route('/<server>/backup/progress', methods=["GET"])
@token_required
@check_server_exists
def get_backup_progress(server):
    """Returns backup progress as percentage"""
    server = servers.getServerByName(server)
    backup_progress = server.getBackupProgress()
    return jsonify({"isBackupping": backup_progress[0], "backupProgress": backup_progress[1]}), 200

@server_routes.route('/<server>/mods', methods=["GET"])
@check_server_exists
def get_mods(server):
    """Puts mods into a zip file and send the zip in response"""
    mod_zips_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'cache', 'mod_zips')
    server = servers.getServerByName(server)
    server.createModsZip()
    return send_from_directory(mod_zips_dir, server.name + ".zip")

@server_routes.route('/<server>/mods/list', methods=["GET"])
@check_server_exists
def get_mods_list(server):
    """Returns list of mod filenames and extracted mod names"""
    server = servers.getServerByName(server)

    return jsonify({"data": server.getModList()}), 200

@server_routes.route('/<server>/mods/search', methods=["GET", "POST"])
@check_server_exists
def search_mod(server):
    """Searches for mods compatible with the server"""
    server = servers.getServerByName(server)
    query = request.form.get("query")
    platform = mod_helper.Platform.CURSEFORGE
    if request.form.get("platform") is not None:
        try:
            platform = mod_helper.Platform[request.form.get("platform").upper()]
        except KeyError:
            pass
    mod_loader = server.server_type.name.lower()
    mods = None
    if platform == mod_helper.Platform.CURSEFORGE:
        mods = mod_helper.search_curseforge_mods(query, mod_loader=mod_loader, version=server.game_version)
    else:
        mods = mod_helper.search_modrinth_mods(query, mod_loader=mod_loader, version=server.game_version)

    mods_json = []
    for mod in mods:
        mods_json.append(mod.to_json())

    return jsonify({"data": mods_json}), 200

@server_routes.route('/<server>/mods/install', methods=["POST"])
@requiresUserPermissionLevel(permissions["install_mod"])
@check_server_exists
def install_mod(server):
    """Installs a mod from Curseforge or Modrinth"""
    server = servers.getServerByName(server)
    platform = mod_helper.Platform.CURSEFORGE
    if request.form.get("platform") is not None:
        # check if it is an integer
        flag = True
        try:
            int(request.form.get("platform"))
        except ValueError:
            flag = False
        if flag:
            if int(request.form.get("platform")) == 1:
                platform = mod_helper.Platform.CURSEFORGE
            else:
                platform = mod_helper.Platform.MODRINTH
        else:
            try:
                platform = mod_helper.Platform[request.form.get("platform").upper()]
            except KeyError:
                pass
    project_id = request.form.get("project_id")
    mods_folder = os.path.join(server.server_location, "mods")

    result = None
    if platform == mod_helper.Platform.CURSEFORGE:
        result = mod_helper.download_curseforge_mod(
            project_id, mods_folder,
            server.server_type.name.lower(),
            server.game_version if server.game_version else "")
    else:
        result = mod_helper.download_modrinth_mod(
            project_id, mods_folder,
            server.server_type.name.lower(),
            server.game_version if server.game_version else "")

    if result[1] != 200:
        return jsonify({"error": result[0]}), 500

    return jsonify({"message": result[0]}), 200

@server_routes.route('/<server>/mods/delete', methods=["POST"])
@requiresUserPermissionLevel(permissions["install_mod"])
@check_server_exists
def delete_mod(server):
    """Deletes a mod from the server."""
    server = servers.getServerByName(server)
    filename = request.form.get("filename")
    path = os.path.join(server.server_location, "mods", filename)
    try:
        os.remove(path)
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 500
    return jsonify({"filename": filename}), 200
