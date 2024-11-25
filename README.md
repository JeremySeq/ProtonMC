
# ProtonMC

A website control panel for Minecraft servers.
Built with Flask and React.

Tested to work on Windows and Linux.

Supports the following servers (+ automated installation) (although others may be possible by installing manually):
- Spigot
- Forge
- NeoForge
- Fabric

## Installation

**Windows and Linux**

1. Download the latest build zipfile.
2. Extract the contents.
3. Run the setup script:
   - **Windows**: `setup.bat`
   - **Linux**: `sudo sh setup.sh`
4. Run the run script:
   - **Windows**: `run.bat`
   - **Linux**: `sudo sh run.sh`


## Development

You must have Python and Node.js installed.

1. Download and extract the repository to a new folder.
2. Install all Python packages from `backend/requirements.txt`.
3. Run `backend/setup.py` from the root directory.
4. Run `backend/main.py` from the root directory. This is your Python backend API.
5. Run `npm run dev` from the `/frontend` directory. This is your Vite + React frontend.
