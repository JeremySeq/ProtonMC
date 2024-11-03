import requests
import os
import subprocess
import jdk_installations

buildtools_folder = os.path.join(os.path.abspath(os.getcwd()), ".buildtools")

def download_spigot_buildtools():
    """
    Downloads BuildTools.jar from Spigot.
    """

    download_link = "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar"

    response = requests.get(download_link)

    if response.status_code == 200:
        if not os.path.exists(buildtools_folder):
            os.makedirs(buildtools_folder)
        with open(os.path.join(buildtools_folder, 'BuildTools.jar'), 'wb') as file:
            file.write(response.content)
            print("BuildTools.jar successfully downloaded.")
            return True
    else:
        print("Failed to download BuildTools.jar.")
        return False

def build_spigot_jar(mc_version):
    """
    Creates a spigot server jar file for the specified Minecraft version using BuildTools.

    Returns:
        The path to the created spigot jar file.
    """

    spigot_jar_path = os.path.join(buildtools_folder, f"spigot-{mc_version}.jar")
    if os.path.exists(spigot_jar_path):
        print("Spigot jar already exists.")
        return spigot_jar_path

    if not download_spigot_buildtools():
        return None
    
    jdk_path = jdk_installations.install_jdk_for_mc_version(mc_version)

    run_buildtools_proc = subprocess.Popen(
        f"{jdk_path}/bin/java.exe -jar BuildTools.jar --rev {mc_version}", 
        cwd=buildtools_folder,
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    buildtools_proc_lines = []

    while run_buildtools_proc.poll() is None:
        line = run_buildtools_proc.stdout.readline()
        line = line.strip()
        if line != "":
            buildtools_proc_lines.append(line)
            print(line.decode('utf-8'))

    spigot_jar_path = os.path.join(buildtools_folder, f"spigot-{mc_version}.jar")

    if not os.path.exists(spigot_jar_path):
        print("Failed to create Spigot jarfile.")
        return None

    return spigot_jar_path

if __name__ == "__main__":
    build_spigot_jar("1.20.1")
