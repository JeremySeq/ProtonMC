"""Main flask application for ProtonMC"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
import servers
import login
from api import api
from frontend import frontend


load_dotenv()
secret_key = os.getenv('SECRET_KEY')

secret_key = os.getenv('SECRET_KEY')
if secret_key is None:
    print("Create the .env file with the SECRET_KEY variable")
    exit()

def create_app(include_frontend=True):
    """Creates the flask application with configurations"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
    CORS(app)

    # register blueprints
    app.register_blueprint(api, url_prefix="/api/")

    # bundles frontend in with the flask app for easier run
    if include_frontend:
        app.register_blueprint(frontend, url_prefix="/")

    servers.initServers()
    login.initUsers()

    return app

if __name__ == '__main__':
    create_app(include_frontend=False).run(host="0.0.0.0", port=5000, debug=False)
