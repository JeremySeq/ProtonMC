"""
1. Copy /backend
2. Remove backend/.env
3. `npm run build` in /frontend
4. Copy frontend/dist
5. Copy permissions.json
6. Copy README.md
9. Create run.bat and setup.bat
"""

import os
import shutil
import subprocess

from colorama import Fore, Style

DIST_FOLDER = os.path.join(os.path.abspath(os.getcwd()), "dist", "ProtonMC")

def run_npm_build():
    """Runs `npm run build` in the frontend folder and prints the output."""
    frontend_folder = os.path.join(os.path.abspath(os.getcwd()), "frontend")
    if not os.path.exists(frontend_folder):
        print("Frontend folder not found. Skipping `npm run build`.")
        return

    try:
        # Change directory to the frontend folder and execute `npm run build`
        process = subprocess.Popen(
            ["npm.cmd", "run", "build"],
            cwd=frontend_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Stream the output
        for line in process.stdout:
            print(line, end="")  # Print each line as it's received

        process.wait()  # Wait for the process to complete

        if process.returncode != 0:
            print("Error: `npm run build` failed. Check the above logs for details.")
        else:
            print("`npm run build` completed successfully.")

    except FileNotFoundError:
        print("Error: `npm` not found. Ensure Node.js and npm are installed.")
    except Exception:
        print("Error: Skipping `npm run build`.")

def build():
    if os.path.exists(DIST_FOLDER):
        print("Delete old build")
        shutil.rmtree(DIST_FOLDER)
    backend_folder = os.path.join(os.path.abspath(os.getcwd()), "backend")

    # copy backend
    shutil.copytree(backend_folder, os.path.join(DIST_FOLDER, "backend"), dirs_exist_ok=True)
    print("Copied backend.")

    # remove .env
    env = os.path.join(DIST_FOLDER, "backend", ".env")
    if os.path.exists(env):
        os.remove(env)

    # build frontend
    # Change directory to the frontend folder and run the build command
    run_npm_build()

    # copy frontend/dist
    frontend = os.path.join(os.path.abspath(os.getcwd()), "frontend", "dist")
    shutil.copytree(frontend, os.path.join(DIST_FOLDER, "frontend", "dist"), dirs_exist_ok=True)
    print("Copied frontend build.")

    # copy permissions.json
    shutil.copy(os.path.join(os.path.abspath(os.getcwd()), "permissions.json"), os.path.join(DIST_FOLDER, "permissions.json"))

    # copy README.md
    shutil.copy(os.path.join(os.path.abspath(os.getcwd()), "README.md"), os.path.join(DIST_FOLDER, "README.md"))

    # system = platform.system()
    # if system == "Windows":
    with open(os.path.join(DIST_FOLDER, "run.bat"), mode="w") as f:
        f.write("\"venv/Scripts/python.exe\" backend/deploy.py")
    with open(os.path.join(DIST_FOLDER, "setup.bat"), mode="w") as f:
        f.writelines([
            "python -m venv venv\n",
            "\"venv/Scripts/pip.exe\" install -r backend/requirements.txt\n",
            "\"venv/Scripts/python.exe\" backend/setup.py"
        ])
    # else:
    with open(os.path.join(DIST_FOLDER, 'run.sh'), 'w', encoding="utf-8") as f:
        f.write("\"venv/bin/python\" backend/deploy.py")
    os.chmod(os.path.join(DIST_FOLDER, 'run.sh'), 0o755)

    with open(os.path.join(DIST_FOLDER, 'setup.sh'), 'w', encoding="utf-8") as f:
        f.writelines([
            "python3 -m venv venv\n",
            "./venv/bin/pip install -r backend/requirements.txt\n",
            "./venv/bin/python backend/setup.py"
        ])
    os.chmod(os.path.join(DIST_FOLDER, 'setup.sh'), 0o755)

    print("Created run scripts.")

    print(Fore.GREEN + "----BUILD COMPLETE----" + Style.RESET_ALL)

if __name__ == "__main__":
    build()
