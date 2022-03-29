from pypresence import Presence
from ursina import *

from modules.player import *
from modules.terrain import *


class CubePixel(Entity):
    def __init__(self):
        self.player = Player(self)

        self.terrain = TerrainMesh(self)

        self.sky = Sky()


if __name__ == '__main__':
    app = Ursina(vsync=False,
                 borderless=False,
                 fullscreen=False,
                 title='CubePixel')

    application.hot_reloader.enabled = False

    try:
        rpc = Presence("873205161747705896")
        rpc.connect()
        rpc.update(state="Playing", large_image="large", start=time.time())
    except:
        print('RPC : Discord not found')

    def input(key):
        if key == 'escape':
            application.quit()

    game = CubePixel()

    app.run()
