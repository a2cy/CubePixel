from ursina import Ursina, Entity, Animator, Vec3, Sky, window

from modules.gui import MainMenu, PauseMenu, LoadingScreen, ExitMenu, DebugScreen
from modules.player import Player
from modules.chunk_handler import ChunkHandler
from modules.settings import settings, parameters
from modules.entity_loader import world_generator, texture_array


class CubePixel(Entity):

    def __init__(self, app, **kwargs):
        super().__init__()
        self.app = app
        self.settings = settings
        self.parameters = parameters

        self.world_generator = world_generator
        self.texture_array = texture_array

        self.main_menu = MainMenu(self)
        self.main_menu.disable()

        self.pause_menu = PauseMenu(self)
        self.pause_menu.disable()

        self.loading_screen = LoadingScreen(self)
        self.loading_screen.disable()

        self.exit_menu = ExitMenu(self)
        self.exit_menu.disable()

        self.debug_screen = DebugScreen(self)
        self.debug_screen.disable()

        self.player = Player(self, position=Vec3(0, 10, 0))
        self.player.disable()

        self.chunk_handler = ChunkHandler(self)

        self.sky = Sky(texture = "sky_default")

        self.ui_state_handler = Animator({
            "None": None,
            "main_menu": self.main_menu,
            "pause_menu": self.pause_menu,
            "loading_screen": self.loading_screen,
            "exit_menu": self.exit_menu
            }, "main_menu"
        )

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == "escape" and self.ui_state_handler.state == "None":
            self.ui_state_handler.state = "pause_menu"
            self.player.disable()

        if key == "k":
            self.chunk_handler.render_distance -= 1

        if key == "i":
            self.chunk_handler.render_distance += 1


def main():
    # pip install --force-reinstall --break-system-packages -r requirements.txt

    # from panda3d.core import loadPrcFileData
    # loadPrcFileData("", "want-pstats 1")
    # loadPrcFileData("", "pstats-python-profiler 1") 

    window.show_ursina_splash = True

    app = Ursina(development_mode=True,
                vsync=settings["vsync"],
                borderless=settings["borderless"],
                fullscreen=settings["fullscreen"],
                title="CubePixel")

    CubePixel(app=app)

    app.run()


if __name__ == "__main__":
    main()
