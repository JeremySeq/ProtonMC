"""Contains routes for controlling Minecraft servers"""
import os
from flask import Blueprint, request, jsonify, send_from_directory
import servers
from loginRoutes import token_required, requiresUserPermissionLevel

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
    """Returns list of server names"""
    s = [server.name for server in servers.servers]
    return s, 200

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
@requiresUserPermissionLevel(2)
@check_server_exists
def get_console(server):
    """Returns console lines"""
    server = servers.getServerByName(server)

    return jsonify(server.console), 200

@server_routes.route('/<server>/console', methods=["POST"])
@token_required
@requiresUserPermissionLevel(4)
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
@requiresUserPermissionLevel(2)
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
