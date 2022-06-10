from ursina import *

from modules.gui import *
from modules.player import *
from modules.world import *
from modules.settings import *
from modules.entity_loader import *


class CubePixel(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.settings = settings
        self.entity_dict = entity_dict

        self.title_screen = TitleScreen(self)
        self.title_screen.enabled = True

        self.pause_screen = PauseScreen(self)
        self.pause_screen.enabled = False

        self.debug_screen = DebugScreen(self)
        self.debug_screen.enabled = False

        self.chunk_handler = ChunkHandler(self)
        self.chunk_handler.enabled = False

        self.player = Player(self)
        self.player.enabled = False

        self.sky = Sky()
        self.sky.enabled = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def join_world(self):
        self.title_screen.enabled = False

        self.debug_screen.enabled = True

        self.chunk_handler.enabled = True
        self.chunk_handler.load_world()

        self.player.enabled = True
        self.player.position = Vec3(0, 10, 0)

        self.sky.enabled = True

    def leave_world(self):
        self.title_screen.enabled = True

        self.debug_screen.enabled = False

        self.pause_screen.enabled = False

        self.chunk_handler.unload_world()
        self.chunk_handler.enabled = False

        self.player.enabled = False

        self.sky.enabled = False

        mouse.locked = False

    def input(self, key):
        if key == "escape" and self.chunk_handler.enabled == True:
            self.pause_screen.enabled = not self.pause_screen.enabled
            mouse.locked = not mouse.locked

    def update(self):
        if self.player.y < -20:
            self.player.y = 10


if __name__ == "__main__":
    app = Ursina(vsync=settings["settings"]["vsync"],
                 borderless=settings["settings"]["borderless"],
                 fullscreen=settings["settings"]["fullscreen"],
                 title="CubePixel")

    application.hot_reloader.enabled = False

    game = CubePixel()

    app.run()
