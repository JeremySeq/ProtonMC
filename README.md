
# ProtonMC

A website control panel for Minecraft servers.
Built with Flask and React.

## Deployment


### Minecraft Server Setup

You should first make sure you have a Minecraft server set up.

**You must have a `run.bat` file in your server folder**. This file will launch the server.

Here's an example of a `run.bat` file for a Spigot server:
```bat
cd "C:\MinecraftServers\MyRandomServer\"
java -Xmx4G -Xms4G -jar server.jar nogui
```

### ProtonMC setup

You must have Python and Node.js installed.

1. Download and extract the repository to a new folder.
2. Install all Python packages from `requirements.txt`.
3. Run `python backend/setup.py` from the root directory.
4. There are a few config and .env files you need to fill in:
    - `servers.json`: all the Minecraft server setup stuff
    - `users.json`: all the user and login stuff
    - `frontend/.env.production`: your IP address (or domain name) of the device you are running this on.
5. Run `npm run build` in the `/frontend` directory to build the frontend.
6. Run `python backend/deploy.py` from the root directory.


## Development

1. Do all [the deployment steps](#deployment) above.
2. Run `python backend/main.py` from the root directory. This is your Python backend API.
3. Run `npm run dev` from the `/frontend` directory. This is your Vite + React frontend.
