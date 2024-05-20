import os
import json


class SettingManager():

    def __init__(self):
        if not os.path.isfile("./settings.json"):
            self.default_settings()

        self.settings, self.parameters = self.load_settings()


    def default_settings(self):
        setting = {
            "vsync": True,
            "borderless": False,
            "fullscreen": False,
            "render_distance": 2,
            "mouse_sensitivity": 90,
            "fov": 90
        }

        with open("./settings.json", "w+") as file:
            json.dump(setting, file, indent=4)


    def load_settings(self):
        with open("./settings.json") as file:
            settings = json.load(file)

        with open("./res/parameters.json") as file:
            parameters = json.load(file)

        return settings, parameters


    def save_settings(self):
        with open("./settings.json", "w+") as file:
            json.dump(self.settings, file, indent=4)

instance = SettingManager()
