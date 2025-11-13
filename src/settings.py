import json
import os


class Settings:
    def __init__(self) -> None:
        if not os.path.isfile("./settings.json"):
            self.default_settings()

        self.settings = self.load_settings()

    def default_settings(self) -> None:
        settings = {"render_distance": 2, "chunk_updates": 2, "mouse_sensitivity": 80, "fov": 90}

        with open("./settings.json", "w+") as file:
            json.dump(settings, file, indent=4)

    def load_settings(self) -> dict:
        with open("./settings.json") as file:
            return json.load(file)

    def save_settings(self) -> None:
        with open("./settings.json", "w+") as file:
            json.dump(self.settings, file, indent=4)


settings = Settings()
