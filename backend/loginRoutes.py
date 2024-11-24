from flask import Blueprint, request, jsonify, current_app
import login
import jwt
import datetime
from flask_login import (
    login_user, 
    login_required, 
    current_user, 
    logout_user
)
from functools import wraps
import permissions

loginRoutes = Blueprint('login', __name__)

def requiresUserPermissionLevel(minPermissionLevel):
    def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                
                token = request.headers.get('Authorization') or request.form.get('Authorization') or request.args.get("Authorization")
                
                if not token:
                    return jsonify({"message": "Token is missing"}), 401
                data = None
                try:
                    token = token.removeprefix('Bearer ')
                    data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms="HS256")
                    if not login.User.get(data["user"]):
                        return jsonify({"message": "Invalid token"}), 401
                except:
                    return jsonify({"message": "Invalid token"}), 401
                
                user = login.User.get(data["user"])
                if (user.permissions < minPermissionLevel):
                    return jsonify({"message": "You do not have permission"}), 403
                return f(*args, **kwargs)
            return decorated
    return decorator

def getUserFromRequest(request):
    token = request.headers.get('Authorization') or request.form.get('Authorization') or request.args.get("Authorization")
                
    if not token:
        return None
    data = None
    try:
        token = token.removeprefix('Bearer ')
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms="HS256")
        if not login.User.get(data["user"]):
            return None
    except:
        return None
    
    user = login.User.get(data["user"])
    return user

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        token = request.headers.get('Authorization') or request.form.get('Authorization') or request.args.get("Authorization")
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            token = token.removeprefix('Bearer ')
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms="HS256")
            if not login.User.get(data["user"]):
                return jsonify({"message": "Invalid token"}), 401
        except:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

@loginRoutes.route("/", methods=["GET"])
@token_required
def getPermissionLevel():
    user = getUserFromRequest(request)
    return jsonify({"username": user.username, "permissions": user.permissions, "permission_set": permissions.permissions}), 200

@loginRoutes.route("/", methods=["POST"])
def loginUser():
    id = request.form.get('username')
    password = request.form.get('password')
    user = login.User.get(id)

    if user and user.password == password:
        token = jwt.encode({"user": id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, current_app.config["SECRET_KEY"])
        print("Logged in user: " + user.username)
        return jsonify({"message": "Logged in", "token": token}), 200

    return jsonify({"message": "Incorrect username and password"}), 401


@loginRoutes.route("/validate", methods=["GET"])
@token_required
def validate():
    user = getUserFromRequest(request)
    return jsonify({"message": "Validated", "username": user.username}), 200

@loginRoutes.route("/logout", methods=["POST"])
@token_required
def getRoute():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

def unauthorized():
    return jsonify({"message": "Unauthorized"}), 401