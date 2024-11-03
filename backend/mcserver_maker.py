import requests
import os
import shutil
import subprocess
from bs4 import BeautifulSoup
import spigot_buildtools
import jdk_installations
from server_types import ServerType


def build_spigot_jar(game_version, destination_folder):
    """
    Builds the Spigot jar using BuildTools and copies it to the destination folder.
    """

    spigot_jar_path = spigot_buildtools.build_spigot_jar(game_version)
    if spigot_jar_path:
        shutil.copy(spigot_jar_path, os.path.join(destination_folder, f"spigot-{game_version}.jar"))
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

def create_run_scripts(server_folder, jdk_path, jar_file, java_gb=4):
    """
    Creates run.bat and run.sh files to run the server jar.

    Args:
        server_folder: The server folder path.
        jdk_path: The path to the JDK installation folder
        jar_file: The path to the server jar file.
        java_gb: The amount of memory to allocate to the server (in GB). Defaults to 4.
    """

    # For Windows, create a run.bat file.
    java_gb = 4
    with open(os.path.join(server_folder, 'run.bat'), 'w', encoding="utf-8") as run_file:
        run_lines = [
            f"cd \"{server_folder}\"",
            f"\"{jdk_path}/bin/java.exe\" -Xmx{java_gb}G -Xms{java_gb}G -jar {jar_file} nogui"
        ]
        run_file.write("\n".join(run_lines))

    # For Linux, create a run.sh file.
    # TODO: test this .sh file on Linux.
    with open(os.path.join(server_folder, 'run.sh'), 'w', encoding="utf-8") as run_file:
        run_lines = [
            f"cd \"{server_folder}\"",
            f"\"{jdk_path}/bin/java\" -Xmx{java_gb}G -Xms{java_gb}G -jar {jar_file} nogui"
        ]
        run_file.write("\n".join(run_lines))

    # Make the script executable
    os.chmod(os.path.join(server_folder, 'run.sh'), 0o755)

def install_spigot_server(server_folder, game_version):
    """
    Installs a Spigot server using BuildTools and creates run.bat and run.sh files.

    Returns:
        True if the server was successfully installed, False otherwise.
    """

    # build the Spigot jar using BuildTools and copy it to the server folder
    if not build_spigot_jar(game_version, server_folder):
        return False

    # Create and setup the run.bat and run.sh files.

    # Get the JDK needed to run this server.
    jdk_path = jdk_installations.install_jdk_for_mc_version(game_version)

    create_run_scripts(server_folder, jdk_path, "server.jar")

    return True

def install_forge_server(server_folder, game_version):
    
    # Forge's API for listing builds (replace "promotions_slim" if URL changes)
    forge_url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
    
    try:
        # Fetch Forge versions JSON
        response = requests.get(forge_url)
        response.raise_for_status()
        data = response.json()
        
        # Get the latest build for the given Minecraft version
        version_key = f"{game_version}-latest"
        if version_key not in data['promos']:
            print(f"No Forge installer found for {game_version}")
            return False
        
        forge_version = data['promos'][version_key]
        download_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{game_version}-{forge_version}/forge-{game_version}-{forge_version}-installer.jar"
        
        # Download the installer JAR
        print(f"Downloading Forge installer for {game_version} (Forge version {forge_version})...")
        jar_response = requests.get(download_url, stream=True)
        jar_response.raise_for_status()
        
        # Save the jar file
        filename = f"forge-{game_version}-{forge_version}-installer.jar"
        with open(os.path.join(server_folder, filename), "wb") as file:
            for chunk in jar_response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Downloaded installer as {filename}")
        
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False
    
    # install the installer jar
    jdk_path = jdk_installations.install_jdk_for_mc_version(game_version)
    jdk_path = os.path.join(jdk_path, "bin", "java")
    run_installer_proc = subprocess.Popen(
        f"{jdk_path} -jar {filename} --installServer {server_folder}", 
        cwd=server_folder,
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    while run_installer_proc.poll() is None:
        line = run_installer_proc.stdout.readline()
        line = line.strip()
        if line != "":
            print(line.decode('utf-8'))

    return True

def install_neoforge_server(server_folder, game_version: str):
    download_url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/"
    
    response = requests.get(download_url)

    soup = BeautifulSoup(response.text, "html.parser")

    directory_elements = soup.find_all(class_="directory")


    target_ver = game_version.removeprefix("1.")

    found_ver = None
    for element in directory_elements:
        ver = element.text.split(".")[0] + "." + element.text.split(".")[1]
        # print(ver)
        if target_ver == ver:
            found_ver = element.text.removesuffix("/")
    
    print(found_ver)
    if found_ver is None:
        print("This version of Neoforge does not exist.")
        return False
    
    download_url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{found_ver}/neoforge-{found_ver}-installer.jar"

    try:
        print(f"Downloading NeoForge server JAR for {game_version}...")
        jar_response = requests.get(download_url, stream=True)
        jar_response.raise_for_status()
        
        # Save the JAR file
        filename = f"neoforge-installer-{game_version}.jar"
        with open(os.path.join(server_folder, filename), "wb") as file:
            for chunk in jar_response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Downloaded server JAR as {filename}")

    except requests.RequestException as e:
        print(f"Error: {e}")
        return False


    # install the installer jar
    jdk_path = jdk_installations.install_jdk_for_mc_version(game_version)
    jdk_path = os.path.join(jdk_path, "bin", "java")
    run_installer_proc = subprocess.Popen(
        f"{jdk_path} -jar {filename} --installServer {server_folder}", 
        cwd=server_folder,
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    while run_installer_proc.poll() is None:
        line = run_installer_proc.stdout.readline()
        line = line.strip()
        if line != "":
            print(line.decode('utf-8'))

    return True

def install_fabric_server(server_folder, game_version):
    # NOTE: This URL might change in the future.
    download_url = f"https://meta.fabricmc.net/v2/versions/loader/{game_version}/0.16.9/1.0.1/server/jar"
    
    try:
        # Download the Fabric server jar
        print(f"Downloading Fabric server JAR for {game_version}...")
        jar_response = requests.get(download_url, stream=True)
        jar_response.raise_for_status()
        
        # Save the JAR file
        filename = f"fabric-server-{game_version}.jar"
        with open(os.path.join(server_folder, filename), "wb") as file:
            for chunk in jar_response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Downloaded server JAR as {filename}")

    except requests.RequestException as e:
        print(f"Error: {e}")
        return False

    # Create the run.bat and run.sh files.
    jdk_path = jdk_installations.install_jdk_for_mc_version(game_version)
    create_run_scripts(server_folder, jdk_path, filename)

    return True

def create_server(name, server_folder, server_type: ServerType, game_version):
    """
    Creates a new folder for the server and installs the server of the specified type.
    Automatically accepts the EULA.

    Args:
        name: Server name, which will be used as the folder name.
        server_folder: Parent folder in which the server will be created. 
            A folder will be created inside this folder with the server name.
        game_version: Minecraft version.
    
    Returns:
        The server folder path.
        False if the server creation failed.
    """

    server_folder = os.path.join(server_folder, name)

    try:
        os.mkdir(server_folder)
    except FileExistsError:
        print("Failed to create server: Folder already exists.")
        return False

    installed = False
    if server_type == ServerType.SPIGOT:
        installed = install_spigot_server(server_folder, game_version)
    elif server_type == ServerType.FORGE:
        installed = install_forge_server(server_folder, game_version)
    elif server_type == ServerType.NEOFORGE:
        installed = install_neoforge_server(server_folder, game_version)
    elif server_type == ServerType.FABRIC:
        installed = install_fabric_server(server_folder, game_version)

    if not installed:
        print("Failed to create the server.")
        os.rmdir(server_folder)
        return False

    accept_eula(server_folder)
    print("Server created successfully.")
    
    return server_folder


if __name__ == "__main__":
    create_server("some_random_server", "J:\\MinecraftServers\\", ServerType.NEOFORGE, "1.20.6")
