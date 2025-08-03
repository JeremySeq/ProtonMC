from flask import request
from flask_socketio import emit

from login import User
from login_routes import getUserFromSocketRequest
from app_instance import socketio, app

class SocketUser:
    def __init__(self, sid, user):
        self.sid = sid
        self.user = user
        self.page_data = {}

    def update_page(self, page_data):
        self.page_data = page_data

    def get_server(self):
        if "serverId" in self.page_data.keys():
            return self.page_data["serverId"]
        return None

connected_users: dict[str, SocketUser] = {}  # sid -> page

@socketio.on("connect")
def handle_connect():
    user: User = getUserFromSocketRequest(request)
    if user is None:
        print(f"Socket client rejected.")
        return False
    print(f"Socket client connected: {request.sid} - {user.username} - {request.remote_addr}")
    connected_users[request.sid] = SocketUser(request.sid, user)
    emit('connected', {'message': 'Connected to ProtonMC WebSocket'})

@socketio.on("page_change")
def handle_page_change(data):
    user_ip = request.remote_addr
    sid = request.sid
    connected_users[sid].update_page(data)
    print(f"User {user_ip} (session {sid}) changed page to: {data}")

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    connected_users.pop(sid, None)
    print(f"User disconnected: {sid}")

def sendSocketMessage(socket_event: str, message: dict, server_id: str = None, page: str = None, dash_page: str = None, permission_level: int = 0):
    """
    Sends message to all users on page (for this server) with given permission level or higher.
    If server_id is None, goes to clients on any server (or server menu).
    If page is None, goes to clients on any page.
    If dash_page is None, goes to clients on any dashboard subpage.
    """
    with app.app_context():
        for user in list(connected_users.values()):
            user_server = user.get_server()
            user_page = user.page_data.get("page")
            user_dash_page = user.page_data.get("dash_page")
            user_permission = user.user.permissions

            if server_id is not None and user_server != server_id:
                continue
            if page is not None and user_page != page:
                continue
            if dash_page is not None and user_dash_page != dash_page:
                continue
            if user_permission < permission_level:
                continue

            print(f"EMIT: {socket_event}, {message}")
            socketio.emit(socket_event, message, to=user.sid)
