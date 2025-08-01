"""Main flask application for ProtonMC"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

import login
import servers
from api import api
from frontend import frontend
from socketio_instance import socketio

load_dotenv()
secret_key = os.getenv('SECRET_KEY')

if secret_key is None:
    print("Create the .env file with the SECRET_KEY variable")
    exit()


def create_app(include_frontend=True):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secret_key
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Enable debug logging for Flask
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Register blueprints etc.
    app.register_blueprint(api, url_prefix="/api/")
    if include_frontend:
        app.register_blueprint(frontend, url_prefix="/")

    servers.initServers()
    login.initUsers()

    return app

app = create_app(include_frontend=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
