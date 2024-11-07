import jdk
import os

jdk_path = os.path.join(os.path.abspath(os.getcwd()), ".jdk")
if not os.path.exists(jdk_path):
    os.makedirs(jdk_path)

def extract_java_version(string: str):
    ver = []
    current_num = ""
    for x in string:
        if x.isdigit():
            current_num += x
        elif current_num != "":
            ver.append(current_num)
            current_num = ""
    if ver[0] == "1":
        return ver[1]
    else:
        return ver[0]

def get_jdk_installations():
    """
    Returns dictionary of installed JDK versions.
    Keys are the major JDK version number,
    and values are the paths to the JDK directories.
    """
    jdks = {}
    for dirpath in os.listdir(jdk_path):
        jdk_ver = extract_java_version(dirpath)
        jdks[jdk_ver] = os.path.join(jdk_path, dirpath)
    return jdks

def install_jdk_for_mc_version(mc_version=None):
    """
    Installs the JDK for the specified Minecraft version.
    If the corresponding JDK is already installed, it will return the path.
    If not, it will download the JDK and return the path.

    Minecraft servers need specific versions of Java to run properly.
    Also, the Spigot Buildtools require specific versions of Java to build.

    https://www.spigotmc.org/wiki/buildtools/#prerequisites

    Returns the installed JDK path.
    """

    
    if mc_version is not None:
        second_num = int(mc_version.split(".")[1])
        third_num = 0
        if (len(mc_version.split(".")) > 2):
            third_num = int(mc_version.split(".")[2])

        version_needed = "21"
        if second_num <= 15:
            version_needed = "8"
        elif second_num <= 17:
            version_needed = "16"
        elif second_num <= 20:
            if (second_num == 20 and third_num >= 5):
                version_needed = "21"
            else:
                version_needed = "17"
        
        jdks = get_jdk_installations()

        if version_needed in jdks:
            print(f"JDK version {version_needed} found.")
            return jdks[version_needed]

        print(f"JDK version {version_needed} not found. Installing...")
        return jdk.install(version_needed, vendor='Corretto', path=jdk_path)
    else:
        return jdk.install("latest", vendor='Corretto', path=jdk_path)

if __name__ == '__main__':
    # print(get_jdk_installations())
    print(install_jdk_for_mc_version("1.19.4"))
