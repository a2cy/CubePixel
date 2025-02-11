import os
import json


class Settings:

    def __init__(self):
        if not os.path.isfile("./settings.json"):
            self.default_settings()

        self.settings = self.load_settings()


    def default_settings(self):
        settings = {
            "render_distance": 2,
            "chunk_updates": 2,
            "mouse_sensitivity": 80,
            "fov": 90
        }

        with open("./settings.json", "w+") as file:
            json.dump(settings, file, indent=4)


    def load_settings(self):
        with open("./settings.json") as file:
            settings = json.load(file)

        return settings


    def save_settings(self):
        with open("./settings.json", "w+") as file:
            json.dump(self.settings, file, indent=4)


instance = Settings()