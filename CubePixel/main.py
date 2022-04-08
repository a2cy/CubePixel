from pypresence import Presence
from ursina import *

from modules.gui import *
from modules.player import *
from modules.terrain import *
from modules.settings import *


class CubePixel(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.rpc = Presence("959187008562008154")
            self.rpc.connect()
            self.rpc.update(state="Playing",
                            large_image="large",
                            start=time.time())
        except:
            print('RPC : Discord not found')

        self.settings = settings
        self.title_screen = TitleScreen(self)

    def start_game(self):
        self.player = Player(self)
        self.player.position = Vec3(0, 10, 0)

        self.terrain = TerrainMesh(self)

        self.sky = Sky()

        self.debug_screen = DebugScreen(self)

        destroy(self.title_screen)

    def return_to_title_screen(self):
        self.title_screen = TitleScreen(self)

        destroy(self.player)

        self.terrain.unload()
        destroy(self.terrain)

        destroy(self.sky)

        destroy(self.debug_screen)

        mouse.locked = False

    def input(self, key):
        if key == 'escape':
            self.return_to_title_screen()


if __name__ == '__main__':
    app = Ursina(vsync=settings.vsync,
                 borderless=settings.borderless,
                 fullscreen=settings.fullscreen,
                 title='CubePixel')

    application.hot_reloader.enabled = False

    game = CubePixel()

    app.run()
