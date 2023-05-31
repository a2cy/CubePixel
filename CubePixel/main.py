import ursina

from modules.gui import MainMenu, PauseMenu, LoadingScreen, DebugScreen
from modules.player import Player
from modules.chunk_handler import ChunkHandler
from modules.settings import settings, parameters
from modules.entity_loader import world_generator, texture_array


class CubePixel(ursina.Entity):

    def __init__(self, profile_mode, **kwargs):
        super().__init__()
        self.settings = settings
        self.parameters = parameters

        self.world_generator = world_generator
        self.texture_array = texture_array

        self.profile_mode = profile_mode

        self.main_menu = MainMenu(self)
        self.main_menu.disable()

        self.pause_menu = PauseMenu(self)
        self.pause_menu.disable()

        self.loading_screen = LoadingScreen(self)
        self.loading_screen.disable()

        self.debug_screen = DebugScreen(self)
        self.debug_screen.disable()

        self.player = Player(self, position=ursina.Vec3(0, 10, 0))
        self.player.disable()

        self.chunk_handler = ChunkHandler(self)
        self.chunk_handler.disable()

        self.sky = ursina.Sky(texture = "sky_default")

        self.ui_state_handler = ursina.Animator({
            "None": None,
            "main_menu": self.main_menu,
            "pause_menu": self.pause_menu,
            "loading_screen": self.loading_screen
            }, "main_menu"
        )

        if self.profile_mode:
            self.ui_state_handler.state = "None"
            self.chunk_handler.enable()
            self.chunk_handler.create_world("profile_world", 1)
            self.debug_screen.enable()
            self.player.enable()
            ursina.mouse.locked = True

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == "escape" and self.ui_state_handler.state == "None":
            self.ui_state_handler.state = "pause_menu"
            self.player.disable()
            ursina.mouse.locked = False


def main():
    # from panda3d.core import loadPrcFileData
    # loadPrcFileData("", "want-pstats 1")
    # loadPrcFileData("", "pstats-python-profiler 1")

    # import faulthandler; faulthandler.enable(all_threads=True)

    # ursina.window.monitor_index = 1

    app = ursina.Ursina(vsync=settings["vsync"],
                        borderless=settings["borderless"],
                        fullscreen=settings["fullscreen"],
                        title="CubePixel")

    ursina.application.hot_reloader.enabled = False
    ursina.window.exit_button.disable()
    ursina.window.fps_counter.disable()

    game = CubePixel(profile_mode=False)

    app.run()


if __name__ == "__main__":
    main()
