import os
import json


def default_settings():
    setting_dict = {
        "vsync": True,
        "borderless": False,
        "fullscreen": False,
        "render_distance": 1,
        "mouse_sensitivity": 90
    }

    with open("./settings.json", "w+") as file:
        json.dump(setting_dict, file, indent=4)


def load_settings():
    with open("./settings.json") as file:
        settings = json.load(file)

    with open("./data/parameters.json") as file:
        parameters = json.load(file)

    return settings, parameters


if not os.path.isfile("./settings.json"):
    default_settings()

settings, parameters = load_settings()
