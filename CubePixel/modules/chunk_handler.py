import os
import json
import numpy as np

from ursina import Entity, destroy, round_to_closest, print_info
from direct.stdpy.threading import Thread
from opensimplex import OpenSimplex

from modules.chunk import Chunk
from modules.shaders import chunk_shader


class ChunkHandler(Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game

        self.amp = self.game.parameters["amp"]
        self.freq2 = self.game.parameters["freq2"]
        self.freq3 = self.game.parameters["freq3"]
        self.chunk_size = self.game.parameters["chunk_size"]
        self.render_distance = self.game.settings["render_distance"]

        if not self.game.settings["generate_caves"]:
            self.freq3 = 0

        self.world_loaded = False
        self.player_chunk = []
        self.chunks_to_update = []
        self.sub_chunks_to_update = []
        self.loaded_chunks = {}
        self.loaded_sub_chunks = {}
        self.cached_sub_chunks = {}

        os.makedirs(f"./saves/", exist_ok=True)

        for key, value in kwargs.items():
            setattr(self, key, value)


    @property
    def render_distance(self):
        return self._render_distance

    @render_distance.setter
    def render_distance(self, value):
        self._render_distance = value
        self.world_size = value * 2 + 1

        if self.world_loaded:
            self.player_chunk = []


    def create_world(self, world_name, seed):
        world_path = f"./saves/{world_name}/"

        if os.path.exists(world_path):
            return False

        os.makedirs(f"{world_path}chunks/", exist_ok=True)
        world_data = {"name": world_name, "seed": round(seed), "player_position": [0, 0, 0]}

        with open(f"{world_path}data.json", "w+") as file:
            json.dump(world_data, file, indent=4)

        self.load_world(world_name)

        return True


    def load_world(self, world_name):
        if self.world_loaded:
            return False

        self.world_path = f"./saves/{world_name}/"

        if not os.path.exists(self.world_path) or not os.path.exists(f"{self.world_path}data.json"):
            return False

        with open(f"{self.world_path}data.json") as file:
            self.world_data = json.load(file)

        self.game.player.position = self.world_data["player_position"]

        self.noise2 = OpenSimplex(self.world_data["seed"]).noise2
        self.noise3 = OpenSimplex(self.world_data["seed"]).noise3

        self.world_loaded = True

        return True


    def unload_world(self):
        if not self.world_loaded:
            return

        if hasattr(self, "update_thread"):
            self.update_thread.join()

        self.world_loaded = False
        self.player_chunk = []
        self.chunks_to_update = []
        self.sub_chunks_to_update = []

        for sub_chunk_id in self.loaded_sub_chunks.copy():
            self.unload_sub_chunk(sub_chunk_id)

        for chunk_id in self.loaded_chunks.copy():
            destroy(self.loaded_chunks.pop(chunk_id))

        with open(f"{self.world_path}data.json", "w+") as file:
            self.world_data["player_position"] = list(self.game.player.position)

            json.dump(self.world_data, file, indent=4)


    def get_chunk_id(self, position):
        return [int(round_to_closest(position[0], self.chunk_size * 3)),
                int(round_to_closest(position[1], self.chunk_size * 3)),
                int(round_to_closest(position[2], self.chunk_size * 3))]


    def load_sub_chunk(self, sub_chunk_id):
        if sub_chunk_id in self.loaded_sub_chunks:
            return

        filename = f"{self.world_path}chunks/{sub_chunk_id}.npy"

        if os.path.exists(filename):
            entities = np.load(filename)

        else:
            entities = self.game.world_generator.generate_chunkentities(self.chunk_size, self.noise2, self.noise3, self.amp, self.freq2, self.freq3, sub_chunk_id)

        self.loaded_sub_chunks[sub_chunk_id] = entities


    def unload_sub_chunk(self, sub_chunk_id):
        if not sub_chunk_id in self.loaded_sub_chunks:
            return

        filename = f"{self.world_path}chunks/{sub_chunk_id}.npy"

        entities = self.loaded_sub_chunks[sub_chunk_id]

        np.save(filename, entities)

        self.loaded_sub_chunks.pop(sub_chunk_id)


    def update_mesh(self):
        chunk_changed = False

        for sub_chunk_id in self.cached_sub_chunks.copy():
            if not sub_chunk_id in self.loaded_sub_chunks:
                self.cached_sub_chunks.pop(sub_chunk_id)

        for chunk_id in self.loaded_chunks:
            sub_chunk_ids = []

            for i in range(3**3):
                x = i // 3 // 3 - 1
                y = i // 3 % 3 - 1
                z = i % 3 - 1

                sub_chunk_id = (chunk_id[0] + x * self.chunk_size,
                                chunk_id[1] + y * self.chunk_size,
                                chunk_id[2] + z * self.chunk_size)

                sub_chunk_ids.append(sub_chunk_id)

            for sub_chunk_id in sub_chunk_ids:
                if sub_chunk_id in self.cached_sub_chunks and not sub_chunk_id in self.sub_chunks_to_update:
                    continue

                vertices, uvs = self.game.world_generator.combine_mesh(self.chunk_size, np.array(sub_chunk_id, dtype=np.intc), self.loaded_sub_chunks[sub_chunk_id])

                sub_chunk = np.stack([vertices, uvs])

                self.cached_sub_chunks[sub_chunk_id] = sub_chunk

                chunk_changed = True

            if chunk_changed:
                chunk = self.loaded_chunks[chunk_id]

                vertices = np.concatenate([self.cached_sub_chunks[chunk_id][0] for chunk_id in sub_chunk_ids], dtype=np.single)
                uvs = np.concatenate([self.cached_sub_chunks[chunk_id][1] for chunk_id in sub_chunk_ids], dtype=np.single)

                chunk.vertices = vertices
                chunk.uvs = uvs

                self.chunks_to_update.append(chunk_id)

        self.sub_chunks_to_update = []


    def update_chunks(self):
        chunk_ids = []
        sub_chunk_ids = []

        for i in range(self.world_size**3):
            x = i // self.world_size // self.world_size - (self.world_size - 1) / 2
            y = i // self.world_size % self.world_size - (self.world_size - 1) / 2
            z = i % self.world_size % self.world_size - (self.world_size - 1) / 2

            chunk_id = (x * 3 * self.chunk_size + self.player_chunk[0],
                        y * 3 * self.chunk_size + self.player_chunk[1],
                        z * 3 * self.chunk_size + self.player_chunk[2])
            
            chunk_ids.append(chunk_id)

        for chunk_id in chunk_ids:
            if not chunk_id in self.loaded_chunks:
                chunk = Chunk(self.chunk_size, chunk_id, shader=chunk_shader)
                chunk.set_shader_input("texture_array", self.game.texture_array)

                self.loaded_chunks[chunk_id] = chunk

        for chunk_id in self.loaded_chunks.copy():
            if not chunk_id in chunk_ids:
                destroy(self.loaded_chunks.pop(chunk_id))

        for chunk_id in chunk_ids:
            for i in range(3**3):
                x = i // 3 // 3 - 1
                y = i // 3 % 3 - 1
                z = i % 3 - 1

                sub_chunk_id = (chunk_id[0] + x * self.chunk_size,
                                chunk_id[1] + y * self.chunk_size,
                                chunk_id[2] + z * self.chunk_size)

                sub_chunk_ids.append(sub_chunk_id)

        for sub_chunk_id in sub_chunk_ids:
            if not sub_chunk_id in self.loaded_sub_chunks:
                self.load_sub_chunk(sub_chunk_id)

        for sub_chunk_id in self.loaded_sub_chunks.copy():
            if not sub_chunk_id in sub_chunk_ids:
                self.unload_sub_chunk(sub_chunk_id)

        self.update_mesh()

        self.game.ui_state_handler.state = "None"


    def update(self):
        if self.chunks_to_update:
            chunk_id = self.chunks_to_update.pop(0)

            if chunk_id in self.loaded_chunks:
                chunk = self.loaded_chunks[chunk_id]
                chunk.update_mesh()

            else:
                print_info(f"chunk {chunk_id} is not loaded")

        player = self.game.player

        new_player_chunk = self.get_chunk_id(player.position)

        thread_alive = self.update_thread.is_alive() if hasattr(self, "update_thread") else False

        if thread_alive or not self.world_loaded or self.chunks_to_update:
            return

        if not self.player_chunk == new_player_chunk:
            self.player_chunk = new_player_chunk

            self.update_thread = Thread(target=self.update_chunks)
            self.update_thread.start()

        elif self.sub_chunks_to_update:
            self.update_thread = Thread(target=self.update_mesh)
            self.update_thread.start()
