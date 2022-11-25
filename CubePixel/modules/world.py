import json
import os
import numpy as np

from direct.stdpy import threading
from opensimplex import OpenSimplex
from ursina import *

from modules.chunk_mesh import ChunkMesh


class ChunkHandler(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__()

        self.amp = self.game.settings["world"]["amp"]
        self.freq = self.game.settings["world"]["freq"]
        self.chunk_with = self.game.settings["world"]["chunk_with"]
        self.render_distance = self.game.settings["settings"]["render_distance"]

        self.chunk_dict = {}
        self.player_chunk = []
        self.updating = False
        self.world_loaded = False

        os.makedirs(f"./saves/", exist_ok=True)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def create_world(self, world_name, seed):
        world_path = f"./saves/{world_name}/"
        
        os.makedirs(f"{world_path}chunks/", exist_ok=True)
        self.world_data = {"name": world_name, "seed": seed}

        with open(f"{world_path}data.json", "w+") as f:
            json.dump(self.world_data, f, indent=4)

        self.load_world(world_name)


    def load_world(self, world_name):
        self.world_path = f"./saves/{world_name}/"

        with open(f"{self.world_path}data.json") as f:
            self.world_data = json.load(f)

        self.noise = OpenSimplex(self.world_data["seed"]).noise2

        self.world_loaded = True


    def unload_world(self):
        self.world_loaded = False
        self.updating = False
        self.update_thread.join()
        self.player_chunk = []

        for chunk_id in self.chunk_dict.copy():
            destroy(self.chunk_dict.pop(chunk_id))


    def generate_chunkentities(self, position):
        entities = np.zeros((self.chunk_with, self.chunk_with, self.chunk_with), np.int16)
        for i in range(self.chunk_with**3):
            x = int(i // self.chunk_with // self.chunk_with - (self.chunk_with - 1) / 2)
            y = int(i // self.chunk_with % self.chunk_with - (self.chunk_with - 1) / 2)
            z = int(i % self.chunk_with % self.chunk_with - (self.chunk_with - 1) / 2)

            max_y = int(self.noise((x + position[0]) / self.freq,
                           (z + position[2]) / self.freq) * self.amp + self.amp / 2)
            
            if y + position[1] == max_y:
                entities[x][y][z] = self.game.entity_index["grass"]
            elif y + position[1] < max_y:
                entities[x][y][z] = self.game.entity_index["stone"]
            else:
                entities[x][y][z] = self.game.entity_index["air"]

        return entities


    def update_chunks(self):
        new_chunk_ids = []

        world_with = self.render_distance * 2 + 1
        for i in range(world_with**3):
            x = i // world_with // world_with - (world_with - 1) / 2
            y = i // world_with % world_with - (world_with - 1) / 2
            z = i % world_with % world_with - (world_with - 1) / 2

            new_chunk_ids.append((int(x * self.chunk_with + self.player_chunk[0]),
                                  int(y * self.chunk_with + self.player_chunk[1]),
                                  int(z * self.chunk_with + self.player_chunk[2])))

        for chunk_id in list(self.chunk_dict.keys()):
            if not chunk_id in new_chunk_ids:
                destroy(self.chunk_dict.pop(chunk_id))

            time.sleep(.002)

        for chunk_id in new_chunk_ids:
            if not self.updating:
                return

            if not chunk_id in self.chunk_dict:
                filename = f"{self.world_path}chunks/{chunk_id}.npy"

                if os.path.exists(filename):
                    entities = np.load(filename)

                else:
                    entities = self.generate_chunkentities(chunk_id)

                    np.save(filename, entities)

                vertex_count = 0
                for entity in self.game.entity_data:
                    if self.game.entity_data[entity] == None:
                        continue
                    
                    vertex_count += len(entities[entities==entity])*len(self.game.entity_data[entity]["vertices"])

                vertices = np.zeros((vertex_count, 3), dtype=np.float32)
                uvs = np.zeros((vertex_count, 2), dtype=np.float32)
                normals = np.zeros((vertex_count, 3), dtype=np.float32)

                entity_data = self.game.entity_data

                slice_index = 0
                for i in range(self.chunk_with**3):
                    x = int(i // self.chunk_with // self.chunk_with - (self.chunk_with - 1) / 2)
                    y = int(i // self.chunk_with % self.chunk_with - (self.chunk_with - 1) / 2)
                    z = int(i % self.chunk_with % self.chunk_with - (self.chunk_with - 1) / 2)
                    entity_position = np.array([x, y, z])
                    model = entity_data[entities[x, y, z]]
                    if model == None:
                        continue

                    new_slice_index = slice_index + len(model["vertices"])

                    vertices[slice_index:new_slice_index] = model["vertices"]+entity_position
                    uvs[slice_index:new_slice_index] = model["uvs"]
                    normals[slice_index:new_slice_index] = model["normals"]

                    slice_index = new_slice_index

                chunk = Entity(parent=self, position=chunk_id, model=ChunkMesh(vertices.ravel(), uvs.ravel(), normals.ravel()), texture="texture_atlas")
                self.chunk_dict[chunk_id] = chunk

        self.updating = False

        if self.game.profile_mode:
            application.quit()


    def update(self):
        player = self.game.player

        new_player_chunk = [int(round_to_closest(player.position[0], self.chunk_with)),
                            int(round_to_closest(player.position[1], self.chunk_with)),
                            int(round_to_closest(player.position[2], self.chunk_with))]

        if self.player_chunk != new_player_chunk and not self.updating and self.world_loaded:
            self.updating = True
            self.player_chunk = new_player_chunk
            self.update_thread = threading.Thread(target=self.update_chunks, args=[])
            self.update_thread.start()
