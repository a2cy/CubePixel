from ursina import Ursina, Entity, Sky, scene

from modules.gui import Gui
from modules.player import Player
from modules.chunk_handler import ChunkHandler
from modules.settings import settings, parameters
from modules.entity_loader import EntityLoader


class Vxyl(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.settings = settings
        self.parameters = parameters

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.entity_loader = EntityLoader()

        self.gui = Gui(self)

        self.player = Player(self)
        self.player.disable()

        self.chunk_handler = ChunkHandler(self)

        self.sky = Sky(parent=scene)

        # temporary stuff

        self.entities = list(self.entity_loader.entity_index.keys())
        self.entities.remove("air")

        self.selected_entity = 0


    def input(self, key):
        keys = [str(i) for i in range(1,10)]
        if key in keys and int(key) <= len(self.entity_loader.entity_data):
            self.selected_entity = int(key)-1

        if key == "left mouse down":
            position = self.player.aim_dot.world_position
            self.chunk_handler.modify_entity(position, self.entity_loader.entity_index["air"])

        if key == "right mouse down":
            position = self.player.aim_dot.world_position
            self.chunk_handler.modify_entity(position, self.entity_loader.entity_index[self.entities[self.selected_entity]])

        if key == "k":
            self.chunk_handler.render_distance -= 1

        if key == "i":
            self.chunk_handler.render_distance += 1

        if key == "n":
            self.player.noclip_mode = not self.player.noclip_mode


    def update(self):
        self.sky.position = self.player.position


if __name__ == "__main__":
    app = Ursina(editor_ui_enabled=False,
                 vsync=settings["vsync"],
                 borderless=settings["borderless"],
                 fullscreen=settings["fullscreen"],
                 title="Vxyl")

    Vxyl()

    app.run()
