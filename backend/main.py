from app_instance import app, socketio
from api import api
from frontend import frontend
import login
import servers

def run_app(host, port, include_frontend=True):
    app.register_blueprint(api, url_prefix='/api/')
    if include_frontend:
        app.register_blueprint(frontend, url_prefix='/')

    servers.initServers()
    login.initUsers()

    print("RUNNING")
    socketio.run(app, host, port)

if __name__ == "__main__":
    run_app(host='0.0.0.0', port=5000, include_frontend=False)