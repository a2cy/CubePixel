import os
import json
import numpy as np

from ursina import Entity, application, round_to_closest

from src.chunk import Chunk
from src.shaders import chunk_shader


class ChunkHandler(Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.updating = False
        self.world_loaded = False
        self.finished_loading = False
        self.player_chunk = ()
        self.chunks_to_load = []
        self.chunks_to_unload = []
        self.chunks_to_update_low = []
        self.chunks_to_update_high = []
        self.loaded_chunks = {}
        self.cached_chunks = {}

        os.makedirs(f"./saves/", exist_ok=True)

        application.base.taskMgr.setupTaskChain("chunk_update", numThreads = 1, frameSync = True)
        application.base.taskMgr.add(self._update, "chunk_update", taskChain = "chunk_update")

        self.mesh = Entity(shader=chunk_shader)
        self.mesh.set_shader_input("texture_array", self.game.entity_loader.texture_array)

        self.amp2d = self.game.parameters["amp2d"]
        self.freq2d = self.game.parameters["freq2d"]
        self.gain2d = self.game.parameters["gain2d"]
        self.octaves2d = self.game.parameters["octaves2d"]
        self.chunk_size = self.game.parameters["chunk_size"]
        self.render_distance = self.game.settings["render_distance"]


    @property
    def render_distance(self):
        return self._render_distance

    @render_distance.setter
    def render_distance(self, value):
        self._render_distance = value
        self.world_size = value * 2 + 1

        if self.world_loaded:
            self.player_chunk = ()


    def create_world(self, world_name, seed):
        world_path = f"./saves/{world_name}/"

        if os.path.exists(world_path):
            return

        os.makedirs(f"{world_path}chunks/", exist_ok=True)
        world_data = {"name": world_name, "seed": seed, "player_position": [0, 0, 0]}

        with open(f"{world_path}data.json", "w+") as file:
            json.dump(world_data, file, indent=4)

        self.load_world(world_name)


    def load_world(self, world_name):
        if self.world_loaded:
            return

        self.world_path = f"./saves/{world_name}/"

        if not os.path.exists(self.world_path) or not os.path.exists(f"{self.world_path}data.json"):
            return

        with open(f"{self.world_path}data.json") as file:
            self.world_data = json.load(file)

        self.game.player.position = self.world_data["player_position"]

        self.seed = self.world_data["seed"]

        self.finished_loading = False
        self.world_loaded = True


    def unload_world(self):
        if not self.world_loaded:
            return

        self.world_loaded = False
        self.player_chunk = ()
        self.chunks_to_load = []
        self.chunks_to_unload = []
        self.chunks_to_update_low = []
        self.chunks_to_update_high = []

        for chunk_id in self.cached_chunks.copy():
            self.unload_chunk(chunk_id)

        for chunk_id in self.loaded_chunks.copy():
            chunk = self.loaded_chunks.pop(chunk_id)
            chunk.remove_node()

        with open(f"{self.world_path}data.json", "w+") as file:
            self.world_data["player_position"] = list(self.game.player.position)

            json.dump(self.world_data, file, indent=4)


    def get_chunk_id(self, position):
        return (int(round_to_closest(position[0], self.chunk_size)),
                int(round_to_closest(position[1], self.chunk_size)),
                int(round_to_closest(position[2], self.chunk_size)))


    def get_entity_id(self, position):
        if not self.world_loaded:
            return

        chunk_id = self.get_chunk_id(position)

        x_position = round(position[0] + (self.chunk_size - 1) / 2 - chunk_id[0])
        y_position = round(position[1] + (self.chunk_size - 1) / 2 - chunk_id[1])
        z_position = round(position[2] + (self.chunk_size - 1) / 2 - chunk_id[2])

        index = x_position * self.chunk_size * self.chunk_size + y_position * self.chunk_size + z_position

        if not chunk_id in self.cached_chunks:
            return

        return self.cached_chunks[chunk_id][index]


    def modify_entity(self, position, entity_id):
        if not self.world_loaded:
            return

        neighbor_ids = []

        chunk_id = self.get_chunk_id(position)

        x_position = round(position[0] + (self.chunk_size - 1) / 2 - chunk_id[0])
        y_position = round(position[1] + (self.chunk_size - 1) / 2 - chunk_id[1])
        z_position = round(position[2] + (self.chunk_size - 1) / 2 - chunk_id[2])

        index = x_position * self.chunk_size * self.chunk_size + y_position * self.chunk_size + z_position

        if not chunk_id in self.cached_chunks:
            return

        self.cached_chunks[chunk_id][index] = entity_id

        for i in range(3 * 2):
            neighbor_id = ((i + 0) % 3 // 2 * (i // 3 * 2 - 1) * self.chunk_size + chunk_id[0],
                           (i + 1) % 3 // 2 * (i // 3 * 2 - 1) * self.chunk_size + chunk_id[1],
                           (i + 2) % 3 // 2 * (i // 3 * 2 - 1) * self.chunk_size + chunk_id[2])

            if not neighbor_id in self.loaded_chunks:
                continue

            neighbor_ids.append(neighbor_id)


        neighbor_ids.append(chunk_id)

        self.chunks_to_update_high.extend(neighbor_ids)


    def load_chunk(self, chunk_id):
        if chunk_id in self.cached_chunks:
            return

        filename = f"{self.world_path}chunks/{chunk_id}.npy"

        if os.path.exists(filename):
            entities = np.load(filename)

        else:
            entities = self.game.entity_loader.world_generator.generate_chunkentities(self.chunk_size, self.game.entity_loader.entity_index, self.seed, self.freq2d, self.gain2d, self.octaves2d, self.amp2d, np.array(chunk_id, dtype=np.intc))

        self.cached_chunks[chunk_id] = entities

        self.chunks_to_update_low.append(chunk_id)


    def unload_chunk(self, chunk_id):
        if not chunk_id in self.cached_chunks:
            return

        filename = f"{self.world_path}chunks/{chunk_id}.npy"

        entities = self.cached_chunks[chunk_id]

        np.save(filename, entities)

        self.cached_chunks.pop(chunk_id)


    def update_chunk(self, chunk_id):
        if not chunk_id in self.loaded_chunks:
            return

        neighbors = np.zeros(6, dtype=np.longlong)

        for i in range(3 * 2):
            neighbor_id = ((i + 0) % 3 // 2 * (i // 3 * 2 - 1) * self.chunk_size + chunk_id[0],
                           (i + 1) % 3 // 2 * (i // 3 * 2 - 1) * self.chunk_size + chunk_id[1],
                           (i + 2) % 3 // 2 * (i // 3 * 2 - 1) * self.chunk_size + chunk_id[2])

            if neighbor_id in self.cached_chunks:
                neighbors[i] = self.cached_chunks[neighbor_id].ctypes.data

        vertices, uvs = self.game.entity_loader.world_generator.combine_mesh(self.chunk_size, np.array(chunk_id, dtype=np.intc), self.cached_chunks[chunk_id], neighbors)

        chunk = self.loaded_chunks[chunk_id]

        chunk.update(vertices, uvs)


    def update_chunks(self):
        chunk_ids = []

        for i in range(self.world_size**3):
            x = i // self.world_size // self.world_size - (self.world_size - 1) / 2
            y = i // self.world_size % self.world_size - (self.world_size - 1) / 2
            z = i % self.world_size % self.world_size - (self.world_size - 1) / 2

            chunk_id = (int(x * self.chunk_size + self.player_chunk[0]),
                        int(y * self.chunk_size + self.player_chunk[1]),
                        int(z * self.chunk_size + self.player_chunk[2]))

            chunk_ids.append(chunk_id)

        for chunk_id in chunk_ids:
            if not chunk_id in self.loaded_chunks:
                chunk = Chunk(self.chunk_size, chunk_id)
                chunk.reparent_to(self.mesh)
                self.loaded_chunks[chunk_id] = chunk

                self.chunks_to_load.append(chunk_id)

        for chunk_id in self.loaded_chunks.copy():
            if not chunk_id in chunk_ids:
                chunk = self.loaded_chunks.pop(chunk_id)
                chunk.remove_node()

                self.chunks_to_unload.append(chunk_id)


    def _update(self, task):
        if not self.world_loaded:
            return task.cont

        self.updating = True

        player = self.game.player

        new_player_chunk = self.get_chunk_id(player.position)

        if self.chunks_to_update_high:
            chunk_id = self.chunks_to_update_high.pop(0)

            self.update_chunk(chunk_id)

        elif self.chunks_to_unload:
            chunk_id = self.chunks_to_unload.pop(0)

            self.unload_chunk(chunk_id)

        elif self.chunks_to_load:
            chunk_id = self.chunks_to_load.pop(0)

            self.load_chunk(chunk_id)

        elif self.chunks_to_update_low:
            chunk_id = self.chunks_to_update_low.pop(0)

            self.update_chunk(chunk_id)

        elif not self.player_chunk == new_player_chunk:
            self.player_chunk = new_player_chunk

            self.update_chunks()

        else:
            self.updating = False
            self.finished_loading = True

        return task.cont
