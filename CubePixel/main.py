from ursina import *

from modules.gui import *
from modules.player import *
from modules.world import *
from modules.settings import *
from modules.entity_loader import *


class CubePixel(Entity):

    def __init__(self, profile_mode, **kwargs):
        super().__init__()
        self.settings = settings
        self.entity_data = entity_data
        self.profile_mode = profile_mode

        self.main_menu = MainMenu(self)
        self.main_menu.disable()

        self.pause_menu = PauseMenu(self)
        self.pause_menu.disable()

        self.debug_screen = DebugScreen(self)
        self.debug_screen.disable()

        self.player = Player(self)
        self.player.disable()

        self.chunk_handler = ChunkHandler(self)
        self.chunk_handler.disable()

        self.sky = Sky(texture = "sky_default")

        self.ui_state_handler = Animator({
            "None" : None,
            "main_menu" : self.main_menu,
            "pause_menu" : self.pause_menu
            }, "main_menu"
        )

        if self.profile_mode:
            self.ui_state_handler.state = "None"
            self.chunk_handler.enable()
            self.chunk_handler.load_world("world")
            self.debug_screen.enable()
            self.player.enable()
            mouse.locked = True

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == "escape" and self.ui_state_handler.state == "None":
            self.ui_state_handler.state = "pause_menu"
            self.player.disable()
            mouse.locked = False


if __name__ == "__main__":
    app = Ursina(vsync=settings["settings"]["vsync"],
                 borderless=settings["settings"]["borderless"],
                 fullscreen=settings["settings"]["fullscreen"],
                 title="CubePixel")

    application.hot_reloader.enabled = False
    window.exit_button.enabled = False
    window.fps_counter.enabled = False

    game = CubePixel(profile_mode=False)

    app.run()
