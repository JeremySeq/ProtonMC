import requests
import os

def download_spigot_jar(version, destination_folder):
    # https://download.getbukkit.org/spigot/spigot-1.20.6.jar

    spigot_download_link = "https://download.getbukkit.org/spigot/spigot-{}.jar"

    version = "1.20.1"

    download_link = spigot_download_link.format(version)

    response = requests.get(download_link)

    if response.status_code == 200:
        with open(os.path.join(destination_folder, 'server.jar'), 'wb') as file:
            file.write(response.content)
            print("Server jar successfully downloaded.")
    else:
        print("Failed to download server jar.")
        return

def create_spigot_server(name):

    # 1. We create the server folder and download .jar file.
    server_folder = "J:\\MinecraftServers\\{}\\"
    server_folder = server_folder.format(name)
    try:
        os.mkdir(server_folder)
    except FileExistsError:
        print("Failed to create server: Folder already exists.")
        return False

    download_spigot_jar("1.20.1", server_folder)

    # 2. We create the eula.txt file and automatically accept the eula.

    with open(os.path.join(server_folder, 'eula.txt'), 'w', encoding="utf-8") as eula_file:
        eula_file.write("eula=true\n")
        print("Eula file created.")

    # 3. We create and setup the run.bat file.

    java_gb = 4
    with open(os.path.join(server_folder, 'run.bat'), 'w', encoding="utf-8") as run_file:
        run_lines = [
            f"cd \"{server_folder}\"",
            f"java -Xmx{java_gb}G -Xms{java_gb}G -jar server.jar nogui"
        ]
        run_file.write("\n".join(run_lines))

    # 4. We return the server folder
    return server_folder
