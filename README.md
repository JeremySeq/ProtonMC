
# ProtonMC

A website control panel for Minecraft servers.
Built with Flask and React.

Tested to work on Windows and Linux.

Supports the following servers (+ automated installation) (although others may be possible by installing manually):
- Spigot
- Forge
- NeoForge
- Fabric

# Getting Started
## Installation
**Windows and Linux**

Prerequisites: **Python**

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


# Users Configuration
User configuration is located in `users.json`.

**You are heavily encouraged to edit the default users.**

**Example `users.json`:**
```json
{
    "admin": {
        "username": "admin",
        "password": "admin123",
        "permissions": 5
    },
   "someRando": {
      "username": "someRando",
      "password": "password",
      "permissions": 4
   }
}
```

The `permissions` property corresponds to actions listed in `permissions.json` which you may change as well.

# Servers Configuration
Server configuration is located in `servers.json`.

As a user, you should never **need** to view or edit the server configuration, although you can.
Only edit this file if you know what you're doing.

**Structure of `servers.json`**
- `servers_folder` - the main server folder in which other servers are created
- `backups_folder` - the main backup folder in which backup folders for specific servers are created
- `servers_list` - list of servers and their info
	- `<server_name>` - name of the server
		- `server_type` - type of server (spigot, forge, neoforge, fabric)
		- `server_folder` - path to server
		- `backup_folder` - path to backups folder in which backups for the server are created
		- `game_version` - version of Minecraft the server is running
		- `notify_bot_settings` (optional) - settings for Telegram notifications
			- `[bot_token, chat_id, notify_mode (optional)}`
            - `notify_mode` - any desired combination of the following
                - `SERVER_EVENTS = 1, PLAYER_CONN_EVENTS = 2, PLAYER_OTHER_EVENTS = 4`

# Telegram Notifications

ProtonMC can send Telegram messages for certain server events. Here's how to set it up.

**Helpful Links:**
[Obtain your Bot Token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
[How to get Telegram Bot Chat ID](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a)
[How to get a Telegram Bot Chat ID](https://stackoverflow.com/a/32572159)

1. Send `/newbot` to *@BotFather* on Telegram
2. You will receive a token that looks like this: `4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc`.
3. Add the bot to a group chat.
4. Open `https://api.telegram.org/bot{our_bot_token}/getUpdates` (replace `our_bot_token` with the token you received earlier).
5. Find the chat ID for the new group chat.
6. Open `servers.json` and add this under the server you want to receive notifications for:

```
"notify_bot_settings": [
	"{bot_token}",
	"{chat_id}",
	"{notify_mode}" // optional
]
```

