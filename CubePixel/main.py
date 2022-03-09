from pypresence import Presence
from ursina import *

from modules.player import *
from modules.terrain import *


class CubePixel(Entity):
    def __init__(self):
        self.cursor = Entity(parent=camera.ui,
                             model='quad',
                             color=color.pink,
                             scale=.008,
                             rotation_z=45)

        self.player = Player(self)

        self.terrain = TerrainMesh(self)

        self.sky = Sky()

        self.camera = EditorCamera(position=Vec3(0, 1, 0))


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
        if key == 'left arrow':
            game.player.x -= 1

        if key == 'right arrow':
            game.player.x += 1

        if key == 'up arrow':
            game.player.y += 1

        if key == 'down arrow':
            game.player.y -= 1

    def update():
        game.terrain.player_position = game.player.position

        if held_keys['escape']:
            application.quit()

    game = CubePixel()

    app.run()
