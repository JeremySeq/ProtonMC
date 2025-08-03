import datetime
import os
import platform
import shutil
import subprocess
import threading
import time
import zipfile
from enum import Enum
from queue import Queue, Empty
from threading import Thread

import progressbar
import psutil

import extract_mod_info
from backend.permissions import permissions
from backend.server_websockets import sendSocketMessage
from server_types import ServerType
import mod_helper
from notify import ServerEvent, NotifyBot
from util import *
import jdk_installations


class MCserver:
    class ServerStatus(Enum):
        STOPPED = 0
        STARTING = 1
        RUNNING = 2
        CREATING = 3

    def __init__(self, name, server_type, server_location, backup_location, notify_bot=None, game_version=None):
        self.server_type = server_type
        self.game_version = game_version
        self.server_location = server_location
        self.backup_location = backup_location
        if notify_bot is None:
            notify_bot = NotifyBot(None, None)
        self.notify_bot = notify_bot
        # create backup folder for server if necessary
        try:
            os.mkdir(self.backup_location)
        except FileExistsError:
            pass
        except FileNotFoundError:
            print(f"Could not find backup folder for server: {name}.")
        self.name = name
        self.console = []
        self.subprocess = None
        self.backup_thread = None
        self.backup_progress = 0
        self.command_queue = Queue()
        self.is_operational = False
        self.players = []

        # self.async_create_backup_directory()

    def __str__(self):
        return self.name

    def async_create_backup_directory(self):
        def try_mkdir():
            try:
                os.mkdir(self.backup_location)
            except FileExistsError:
                pass
            except FileNotFoundError:
                print(f"Could not find backup folder for server: {self.name}.")

        thread = threading.Thread(target=try_mkdir)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.runCommand("stop")

    def runCommand(self, command):
        if not self.isServerRunning():
            print("Server is not running")
            return False
        print(command)
        self.command_queue.put(command)
        return True

    def getBackupProgress(self) -> list[bool, int]:
        if self.backup_thread is None:
            return False, 0
        if self.backup_thread.is_alive:
            return True, self.backup_progress
        return False, 0

    def startBackup(self):
        self.backup_thread = Thread(target=self.backupBlocking)
        # self.backup_thread.daemon = True
        self.backup_thread.start()

    def backupBlocking(self):
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        year = datetime.datetime.now().year
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute

        a = self.server_location
        b = f'{self.backup_location}\\{month}-{day}-{year}_{hour}-{minute}'
        # os.mkdir(b)

        try:
            self.zip_folder_for_backup(a, self.backup_location, f"{month}-{day}-{year}_{hour}-{minute}.zip")
        except FileNotFoundError:
            # TODO: backup errors like this are not communicated to the frontend
            print("Failed backup: FileNotFoundError")
            self.backup_thread = None
            return

        # self.copy(a, b)
        print("Done backup.")
        self.backup_thread = None

    def zip_folder_for_backup(self, folder_path, zip_dest_folder, zip_filename):
        # Create the full path for the zip file
        zip_file_path = os.path.join(zip_dest_folder, zip_filename)

        # get total file count and folder size
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(folder_path):
            file_count += len(files)
            total_size += sum(os.path.getsize(os.path.join(root, file)) for file in files)

        # Convert total size to megabytes
        total_size_mb = total_size / (1024 * 1024)

        widgets = [' [',
                   progressbar.Timer(format='Elapsed Time: %(elapsed)s'),
                   '] ',
                   progressbar.Bar('*'), ' (',
                   progressbar.ETA(), ') ',
                   ]
        bar = progressbar.ProgressBar(max_value=total_size_mb,
                                      widgets=widgets).start()

        # Create a zip file
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the directory
            count = 0
            size_written = 0
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    # Create the full path of the file
                    file_path = os.path.join(root, file)

                    count += 1
                    # get the size of the file
                    file_size = os.path.getsize(file_path)
                    # update the size written
                    size_written += file_size
                    # convert size written to megabytes
                    size_written_mb = size_written / (1024 * 1024)
                    # update the progressbar
                    try:
                        bar.update(size_written_mb)
                    except ValueError:
                        print("Error updating progress bar. Size written exceeded expected value. Ignoring...")

                    self.backup_progress = bar.percentage

                    # Add file to the zip file
                    try:
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))
                    except:
                        print("Error writing file: " + file)

        bar.finish()
        self.backup_progress = 0

    def restore(self, backup_name):
        self.delete(self.server_location)
        path = f"{self.backup_location}\\{backup_name}"
        self.copy(path, self.server_location)

        print("Restored backup.")

    def copy(self, origin, target):
        print("Copying {} to {}".format(origin, target))
        files = os.listdir(origin)
        for file_name in files:
            try:
                src = f"{origin}\\{file_name}"
                dst = f"{target}\\{file_name}"
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    os.mkdir(dst)
                    self.copy(src, dst)
            except PermissionError:
                print("Permission Error...continuing")

    def delete(self, target):
        files = os.listdir(target)
        for file_name in files:
            file = f"{target}\\{file_name}"
            if os.path.isfile(file):
                os.remove(file)
            elif os.path.isdir(file):
                self.delete(file)
                os.rmdir(file)

    def createFile(self, dir, name, content):
        path = f"{self.server_location}{dir}\\{name}"
        file = open(path, 'wb')
        file.write(content)
        file.close()

    def appendFile(self, dir, name, content):
        path = f"{self.server_location}{dir}\\{name}"
        try:
            file = open(path, 'ab')
            file.write(content)
        except FileNotFoundError:
            file = open(path, 'wb')
            file.write(content)
        file.close()

    def getBackups(self):

        files = os.listdir(self.backup_location)

        stripped = []
        for file in files:
            stripped.append(file.removesuffix('.zip'))

        files = stripped

        def get_datetime(entry):
            templist = entry.split("_")
            date = templist[0].split('-')
            time = templist[1].split('-')

            month = int(date[0])
            day = int(date[1])
            year = int(date[2])
            hour = int(time[0])
            minute = int(time[1])
            return datetime.datetime(year, month, day, hour, minute)

        sorted_backups = sorted(files, key=get_datetime, reverse=True)

        return sorted_backups

    def getServerProperties(self):
        path = f"{self.server_location}\\server.properties"
        file = open(path, 'r')
        propertiesDict = {}
        for x in file.readlines():
            # ignore comments at beginning of server.properties file
            if x.startswith("#"):
                continue

            if (x.startswith("rcon.password") or x.startswith("rcon.port") or x.startswith(
                    "query.port") or x.startswith("server-ip")):
                continue

            templist = x.strip().split('=')
            propertiesDict[templist[0]] = templist[1]
        return propertiesDict

    def changeServerProperties(self, newProperties: dict):
        path = f"{self.server_location}\\server.properties"
        file = open(path, 'r')
        newList = file.readlines()

        # Set newList with newProperties
        for key in newProperties:
            value = newProperties[key]

            for x in newList:
                if x.startswith("#"):
                    continue
                if x.strip().split("=")[0] == key:
                    newList[newList.index(x)] = f"{key}={value}\n"

        # Write entire list to file
        file.close()
        file = open(path, 'w')
        file.write("".join(newList))
        file.close()

    def getFilesInFolder(self, folder):
        dir = f"{self.server_location}\\{folder}"
        files = os.listdir(dir)
        filesDict = {}
        for file_name in files:
            file_loc = f"{dir}\\{file_name}"
            if os.path.isfile(file_loc):
                filesDict[file_name] = "file"
            elif os.path.isdir(file_loc):
                filesDict[file_name] = "folder"

        return filesDict

    def createModsZip(self):
        zf = zipfile.ZipFile(f"cache/mod_zips/{self.name}.zip", "w")
        for dirname, subdirs, files in os.walk(os.path.join(self.server_location, "mods")):
            for filename in files:
                zf.write(os.path.join(dirname, filename), arcname=filename)
        zf.close()

    def hasModsFolder(self):
        if os.path.exists(os.path.join(self.server_location, "mods")):
            return True
        else:
            return False

    def startServerThread(self):
        thread = Thread(target=self.startServerBlocking)
        thread.daemon = True
        thread.start()

    def isServerRunning(self) -> bool:
        if self.subprocess is None:
            return False
        if self.subprocess.poll() is None:
            return True
        return False

    # different than isServerRunning() because it checks if the server has finished startup and can be joined
    def isServerOperational(self) -> bool:
        if not self.isServerRunning():
            return False
        if self.is_operational:
            return True
        if self.isServerRunning():
            for line in self.console:
                if "[Server thread/INFO]" in line and "Done" in line:
                    self.is_operational = True
                    self.notify_bot.notify(ServerEvent.SERVER_STARTED, self.name)
                    return True
            return False
        return False

    def getServerStatus(self):
        running = self.isServerRunning()
        operational = self.isServerOperational()

        if not running:
            return MCserver.ServerStatus.STOPPED

        if not operational:
            return MCserver.ServerStatus.STARTING

        return MCserver.ServerStatus.RUNNING

    def getStartTime(self):
        if not self.isServerRunning():
            return False

        p = psutil.Process(self.subprocess.pid)
        return p.create_time()

    def getUptime(self):
        if not self.isServerRunning():
            return False

        p = psutil.Process(self.subprocess.pid)

        current_time = time.time()
        start_time = p.create_time()

        # Calculate the elapsed time
        elapsed_time = current_time - start_time

        # Convert elapsed time to a readable format (e.g., seconds)
        elapsed_seconds = int(elapsed_time)

        # Format it in hours, minutes, and seconds
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours}:{minutes:02}:{seconds:02}"

    def startServerBlocking(self):

        self.notify_bot.notify(ServerEvent.SERVER_STARTING, self.name)

        # clear console: this is necessary so that isServerOperational doesn't find "Done" in the console from the previous run
        self.console.clear()

        self.players.clear()

        # set operational status as false in case it was true before
        self.is_operational = False

        java_path = jdk_installations.install_jdk_for_mc_version(self.game_version)

        # Use run.bat or run.sh file (depending on the operating system)
        system = platform.system()
        # windows: run.bat
        if system == "Windows":
            os.environ["JAVA_HOME"] = java_path
            serverRunPath = os.path.join(self.server_location, "run.bat")

            self.subprocess = subprocess.Popen(
                [serverRunPath, "nogui"],
                cwd=self.server_location,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        else:  # linux/mac: run.sh
            os.environ["JAVA_HOME"] = java_path
            os.environ["PATH"] = f"{java_path}/bin:" + os.environ["PATH"]
            serverRunPath = os.path.join(self.server_location, "run.sh")

            self.subprocess = subprocess.Popen(
                ["sh", serverRunPath, "nogui"],
                cwd=self.server_location,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

        def server_read_lines(process, queue):
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                queue.put(line.decode('utf-8', errors='replace'))

        qs = Queue()
        ts = Thread(target=server_read_lines, args=(self.subprocess, qs))
        ts.daemon = True
        ts.start()

        try:
            while self.subprocess.poll() is None:

                try:
                    line = self.command_queue.get_nowait()
                except Empty:
                    pass
                else:
                    if line != None:
                        self.subprocess.stdin.write(bytes(line + "\n", encoding="utf-8"))
                        self.subprocess.stdin.flush()
                try:
                    line = qs.get_nowait()
                except Empty:
                    pass
                else:
                    if line:
                        print(line.strip())
                        line = line.strip()

                        if "Server thread/INFO" in getConsoleTags(line):
                            text_after_tags = getTextAfterTags(line)
                            if didPlayerJoin(text_after_tags):
                                self.players.append(didPlayerJoin(text_after_tags))

                                self.notify_bot.notify(ServerEvent.PLAYER_JOIN, didPlayerJoin(text_after_tags))
                                print("PLAYER JOINED:", didPlayerJoin(text_after_tags))
                            if didPlayerLeave(text_after_tags):
                                if didPlayerLeave(text_after_tags) in self.players:
                                    self.players.remove(didPlayerLeave(text_after_tags))

                                self.notify_bot.notify(ServerEvent.PLAYER_LEAVE, didPlayerLeave(text_after_tags))
                                print("PLAYER LEFT:", didPlayerLeave(text_after_tags))

                            if didPlayerGotAchivement(text_after_tags) is not None:
                                self.notify_bot.notify(ServerEvent.PLAYER_ACHIEVEMENT,
                                                       *didPlayerGotAchivement(text_after_tags))

                        line = hideIPIfPlayerJoined(line)
                        line = line.strip()
                        self.console.append(line)
                        sendSocketMessage("console", {"server": self.name, "line": line}, self.name,
                                          "server_dashboard", "console", permission_level=permissions["view_console"])
        finally:
            self.players.clear()
            print("Subprocess ended, joining thread.")
            ts.join(timeout=5)  # Add timeout to ensure the thread doesn't hang
            if ts.is_alive():
                print("Thread did not terminate in time, forcefully terminating.")
            else:
                print("Thread joined, server blocking method exiting.")

            self.notify_bot.notify(ServerEvent.SERVER_STOPPED, self.name)

    def isModded(self):
        modded = [ServerType.FORGE, ServerType.NEOFORGE, ServerType.FABRIC]
        if self.server_type in modded:
            return True
        return False

    def getModType(self):
        """
        Returns either MODS, PLUGINS, or NONE
        """

        modded = [ServerType.FORGE, ServerType.NEOFORGE, ServerType.FABRIC]
        plugin = [ServerType.SPIGOT]

        if self.server_type in modded:
            return mod_helper.ModType.MOD
        elif self.server_type in plugin:
            return mod_helper.ModType.PLUGIN
        else:
            return mod_helper.ModType.NONE

    def getModList(self):
        """Returns list of mods in the server's mods folder. 
        [(file_name, mod_name), etc.] where file_name is the jarfile name,
        and mod_name is the extracted mod name from the mod metadata"""

        results = []
        mods_folder = os.path.join(
            self.server_location,
            "mods" if self.getModType() == mod_helper.ModType.MOD else "plugins"
        )

        for file in os.listdir(mods_folder):
            path = os.path.join(mods_folder, file)
            if os.path.isfile(path) and file.endswith(".jar"):
                try:
                    mod_name = extract_mod_info.get_mod_name(path)
                except Exception as e:
                    print(e)
                    print("Error while extracting mod metadata.")
                    mod_name = file
                results.append((file, mod_name))

        return results
