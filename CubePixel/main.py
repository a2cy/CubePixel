from pypresence import Presence
from ursina import *

from modules.gui import *
from modules.player import *
from modules.terrain import *


class CubePixel(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_screen = TitleScreen(self)

    def start_game(self):
        self.player = Player(self)

        self.terrain = TerrainMesh(self)

        self.sky = Sky()

        destroy(self.title_screen)

    def return_to_title_screen(self):
        self.title_screen = TitleScreen(self)

        destroy(self.player)

        destroy(self.terrain)

        destroy(self.sky)

        mouse.locked = False

    def input(self, key):
        if key == 'escape':
            self.return_to_title_screen()


if __name__ == '__main__':
    app = Ursina(vsync=False,
                 borderless=False,
                 fullscreen=False,
                 title='CubePixel',
                 icon='CubePixel.png')

    application.hot_reloader.enabled = False

    try:
        rpc = Presence("959187008562008154")
        rpc.connect()
        rpc.update(state="Playing", large_image="large", start=time.time())
    except:
        print('RPC : Discord not found')

    game = CubePixel()

    app.run()
