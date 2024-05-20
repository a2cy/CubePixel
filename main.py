from ursina import Ursina

from src.settings_manager import instance as settings_manager


app = Ursina(development_mode=True,
             vsync=settings_manager.settings["vsync"],
             borderless=settings_manager.settings["borderless"],
             fullscreen=settings_manager.settings["fullscreen"],
             title="CubePixel")

from src.gui import instance # starts game

app.run()
