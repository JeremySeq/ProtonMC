from typing import Dict, Optional
import json

from flask_login import (
    UserMixin,
)

users: Dict[str, "User"] = {}

def initUsers():
    with open("users.json") as file:
        data = json.load(file)
        for key in data:
            users[key] = User(
                id=key,
                username=data[key]["username"],
                password=data[key]["password"],
                permissions=data[key]["permissions"]
            )

class User(UserMixin):
    def __init__(self, id: str, username: str, password: str, permissions: int):
        self.id = id
        self.username = username
        self.password = password
        self.permissions = permissions

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        return users.get(user_id)

    def __str__(self) -> str:
        return f"<Id: {self.id}, Username: {self.username}>"

    def __repr__(self) -> str:
        return self.__str__()
