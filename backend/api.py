"""contains API routes"""

from flask import Blueprint
from server_routes import server_routes
from login_routes import loginRoutes

api = Blueprint('api', __name__)


api.register_blueprint(server_routes, url_prefix="servers/")
api.register_blueprint(loginRoutes, url_prefix="login/")
