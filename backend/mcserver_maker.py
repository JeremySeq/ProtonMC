import requests
import os
import shutil
import spigot_buildtools
import jdk_installations


def build_spigot_jar(version, destination_folder):
    """
    Builds the Spigot jar using BuildTools and copies it to the destination folder.
    """

    spigot_jar_path = spigot_buildtools.build_spigot_jar(version)
    if spigot_jar_path:
        shutil.copy(spigot_jar_path, os.path.join(destination_folder, 'server.jar'))
        return True
    
    return False

def download_spigot_jar_using_getbukkit(version, destination_folder):
    """
    May not work anymore because getbukkit.org is down.
    """

    spigot_download_link = "https://download.getbukkit.org/spigot/spigot-{}.jar"

    download_link = spigot_download_link.format(version)

    response = requests.get(download_link)

    if response.status_code == 200:
        with open(os.path.join(destination_folder, 'server.jar'), 'wb') as file:
            file.write(response.content)
            print("Server jar successfully downloaded.")
    else:
        print("Failed to download server jar.")
        return
    
def accept_eula(server_folder):
    """
    Used to automatically accept Minecraft server EULA.
    Creates a eula.txt file in the server folder and sets eula=true.
    """

    with open(os.path.join(server_folder, 'eula.txt'), 'w', encoding="utf-8") as eula_file:
        eula_file.write("eula=true\n")
        print("Eula file created.")

def create_spigot_server(name, server_folder, game_version):
    """
    Creates a Spigot server.
    Creates a new folder for the server and builds the server jar.
    Automatically accepts the EULA.
    Creates a run.bat file to run the server (using a ProtonMC JDK installation).

    Args:
        name: Server name, which will be used as the folder name.
        server_folder: Folder in which the server will be created. 
            A folder will be created inside this folder with the server name.
        game_version: Minecraft version.
    
    Returns:
        The server folder path.
    """

    # 1. We create the server folder and download .jar file.

    server_folder = os.path.join(server_folder, name)

    try:
        os.mkdir(server_folder)
    except FileExistsError:
        print("Failed to create server: Folder already exists.")
        return False

    if not build_spigot_jar(game_version, server_folder):
        return False

    # 2. We create the eula.txt file and automatically accept the eula.

    accept_eula(server_folder)

    # 3. We create and setup the run.bat file.

    # Get the JDK needed to run this server.
    jdk_path = jdk_installations.install_jdk_for_mc_version(game_version)

    # For Windows, create a run.bat file.
    java_gb = 4
    with open(os.path.join(server_folder, 'run.bat'), 'w', encoding="utf-8") as run_file:
        run_lines = [
            f"cd \"{server_folder}\"",
            f"\"{jdk_path}/bin/java.exe\" -Xmx{java_gb}G -Xms{java_gb}G -jar server.jar nogui"
        ]
        run_file.write("\n".join(run_lines))

    # For Linux, create a run.sh file.
    # TODO: test this .sh file on Linux.
    with open(os.path.join(server_folder, 'run.sh'), 'w', encoding="utf-8") as run_file:
        run_lines = [
            f"cd \"{server_folder}\"",
            f"\"{jdk_path}/bin/java\" -Xmx{java_gb}G -Xms{java_gb}G -jar server.jar nogui"
        ]
        run_file.write("\n".join(run_lines))

    # Make the script executable
    os.chmod(os.path.join(server_folder, 'run.sh'), 0o755)

    # 4. We return the server folder
    return server_folder

if __name__ == "__main__":
    create_spigot_server("some_random_server", "J:\\MinecraftServers\\", "1.16.5")
