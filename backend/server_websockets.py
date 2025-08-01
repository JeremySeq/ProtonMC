from flask import request
from flask_socketio import emit

from login import User
from login_routes import getUserFromSocketRequest
from socketio_instance import socketio


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
    print(f"Socket client connected: {request.sid} - {user.username}")
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
