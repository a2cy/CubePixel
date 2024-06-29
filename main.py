from ursina import Ursina, color, window

from src.settings import instance as settings

app = Ursina(development_mode=True,
             vsync=settings.settings["vsync"],
             borderless=settings.settings["borderless"],
             fullscreen=settings.settings["fullscreen"],
             title="CubePixel")

window.color = color.black

from src.gui import instance # starts game

app.run()
