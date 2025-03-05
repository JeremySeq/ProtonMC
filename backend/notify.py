import json
import os
from enum import IntFlag, StrEnum

import telebot
from dotenv import load_dotenv

load_dotenv()
lang = os.getenv("LANG")

# load language dict
lang_file_path = os.path.join(os.getcwd(), "backend", "lang", lang + ".json")
if not os.path.exists(lang_file_path):
    raise FileNotFoundError("Could not find lang file. Check .env LANG property.")
with open(lang_file_path) as lang_file:
    language_dict = json.load(lang_file)

class ServerEvent(StrEnum):
    SERVER_STARTING = "server_starting"
    SERVER_STARTED = "server_started"
    SERVER_STOPPED = "server_stopped"
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_ACHIEVEMENT = "player_achievement"
    PLAYER_DEATH = "player_death"


class NotifyMode(IntFlag):
    SERVER_EVENTS = 1
    PLAYER_CONN_EVENTS = 2
    PLAYER_OTHER_EVENTS = 4


class NotifyBot:
    def __init__(self, token, chat_id, notify_mode=None):
        self.__token = token
        if token is not None:
            self._bot = telebot.TeleBot(self.__token)
        self.chat_id = chat_id

        if notify_mode is None:
            notify_mode = NotifyMode.SERVER_EVENTS + NotifyMode.PLAYER_CONN_EVENTS + NotifyMode.PLAYER_OTHER_EVENTS

        self.notify_mode = notify_mode

    def get_settings(self):
        return self.__token, self.chat_id,

    def notify(self, event, *args):
        if self.__token is None or self.__token == "":
            return

        if event in (ServerEvent.SERVER_STARTING, ServerEvent.SERVER_STARTED, ServerEvent.SERVER_STOPPED):
            if self.notify_mode & NotifyMode.SERVER_EVENTS:
                self.__send_message(event, *args)

        elif event in (ServerEvent.PLAYER_JOIN, ServerEvent.PLAYER_LEAVE):
            if self.notify_mode & NotifyMode.PLAYER_CONN_EVENTS:
                self.__send_message(event, *args)

        elif event in (ServerEvent.PLAYER_ACHIEVEMENT, ServerEvent.PLAYER_DEATH):
            if self.notify_mode & NotifyMode.PLAYER_OTHER_EVENTS:
                self.__send_message(event, *args)

    def __send_message(self, event, *args):
        try:
            if self.__token is None or self.__token == "":
                return

            self._bot.send_message(self.chat_id, language_dict["server_event." + event.value].format(*args))
        except Exception as e:
            print(e)
            print("Failed to send Telegram message. Ignoring.")
