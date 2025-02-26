from enum import IntEnum, IntFlag

import telebot
import os
from dotenv import load_dotenv

load_dotenv()
lang = os.getenv("LANG")


class ServerEvent(IntEnum):
    SERVER_STARTING = 1
    SERVER_STARTED = 2
    SERVER_STOPPED = 3
    PLAYER_JOIN = 4
    PLAYER_LEAVE = 5
    PLAYER_ACHIEVEMENT = 6
    PLAYER_DEATH = 7


class NotifyMode(IntFlag):
    SERVER_EVENTS = 1
    PLAYER_CONN_EVENTS = 2
    PLAYER_OTHER_EVENTS = 4


local_dict = {'EN': {
    ServerEvent.SERVER_STARTING: 'Server "{}" starting',
    ServerEvent.SERVER_STARTED: 'Server "{}" started',
    ServerEvent.SERVER_STOPPED: 'Server "{}" stopped',
    ServerEvent.PLAYER_JOIN: 'Player {} join',
    ServerEvent.PLAYER_LEAVE: 'Player {} leave',
    ServerEvent.PLAYER_ACHIEVEMENT: 'Player {} got achievement "{}"',
    ServerEvent.PLAYER_DEATH: '{}'
}, 'RU': {
    ServerEvent.SERVER_STARTING: 'Сервер "{}" запускается',
    ServerEvent.SERVER_STARTED: 'Сервер "{}" запущен',
    ServerEvent.SERVER_STOPPED: 'Сервер "{}" остановлен',
    ServerEvent.PLAYER_JOIN: 'Игрок {} присоединился',
    ServerEvent.PLAYER_LEAVE: 'Игрок {} покинул игру',
    ServerEvent.PLAYER_ACHIEVEMENT: 'Игрок {} получил достижение "{}"',
    ServerEvent.PLAYER_DEATH: '{}'
}}


class NotifyBot:
    def __init__(self, token, chat_id, notify_mode=None):
        self.__token = token
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
        if self.__token is None or self.__token == "":
            return

        self._bot.send_message(self.chat_id, local_dict[lang][event].format(*args))
