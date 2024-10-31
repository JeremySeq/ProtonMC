import json

def get_permissions_json():
    with open("permissions.json", "r", encoding="utf-8") as f:
        return json.load(f)

permissions = get_permissions_json()
