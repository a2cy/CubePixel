import json
import os

from direct.stdpy import threading
from opensimplex import OpenSimplex
from ursina import *


class ChunkHandler(Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game
        self.settings = self.game.settings

        for key, value in kwargs.items():
            setattr(self, key, value)

    def load_world(self, world="world", seed=round(time.time())):
        self.world_path = f"saves/{world}/"

        if not os.path.exists(self.world_path):
            os.makedirs(f"{self.world_path}chunks/", exist_ok=False)
            data_dict = {"name": world, "seed": seed}

            with open(f"{self.world_path}data.json", "w+") as f:
                json.dump(data_dict, f, indent=4)

        with open(f"{self.world_path}data.json") as f:
            self.world_data = json.load(f)

        self.seed = self.world_data["seed"]
        self.noise = OpenSimplex(seed=self.seed).noise2
        self.amp = self.game.settings["world"]["amp"]
        self.freq = self.game.settings["world"]["freq"]
        self.chunk_with = self.game.settings["world"]["chunk_with"]
        self.render_distance = self.game.settings["settings"]["render_distance"]

        self.chunk_dict = {}
        self.player_chunk = ()
        self.updating = False

    def unload_world(self):
        self.updating = False
        self.update_thread.join()
        for chunk_id in self.chunk_dict.copy():
            destroy(self.chunk_dict.pop(chunk_id))

    def update(self):
        player = self.game.player

        new_player_chunk = (int(round_to_closest(player.position[0], self.chunk_with)),
                            int(round_to_closest(player.position[1], self.chunk_with)),
                            int(round_to_closest(player.position[2], self.chunk_with)))

        if self.player_chunk != new_player_chunk and not self.updating:
            self.updating = True
            self.player_chunk = new_player_chunk
            self.update_thread = threading.Thread(target=self.update_chunks, args=[])
            self.update_thread.start()

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
            if chunk_id not in new_chunk_ids:
                destroy(self.chunk_dict.pop(chunk_id))

        for chunk_id in new_chunk_ids:
            if not self.updating:
                return

            if not chunk_id in self.chunk_dict:
                filename = f"{self.world_path}chunks/{chunk_id}.json"

                if os.path.exists(filename):
                    with open(filename) as f:
                        entities = json.load(f)

                    chunk = Chunk(self.game, parent=self, position=chunk_id)
                    chunk.entities = entities
                    chunk.generate_chunk()
                    self.chunk_dict[chunk_id] = chunk

                else:
                    chunk = Chunk(self.game, parent=self, position=chunk_id)
                    chunk.entities = self.get_chunkentities(chunk_id)
                    chunk.generate_chunk()
                    self.chunk_dict[chunk_id] = chunk

                    with open(filename, "w+") as f:
                        json.dump(chunk.entities, f)

        self.updating = False

    def get_chunkentities(self, pos):
        entities = {}
        for i in range(self.chunk_with**3):
            x = i // self.chunk_with // self.chunk_with - (self.chunk_with - 1) / 2
            y = i // self.chunk_with % self.chunk_with - (self.chunk_with - 1) / 2
            z = i % self.chunk_with % self.chunk_with - (self.chunk_with - 1) / 2

            max_y = int(self.noise((x + pos[0]) / self.freq,
                           (z + pos[2]) / self.freq) * self.amp + self.amp / 2)
            
            if y + pos[1] <= max_y:
                entities[f"{x} {y} {z}"] = {
                    "name": "grass",
                    "rotation": (0, 0, 0)
                }

            else:
                entities[f"{x} {y} {z}"] = {
                    "name": "air",
                    "rotation": (0, 0, 0)
                }

        return entities


class Chunk(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        self.entities = {}
        super().__init__(model=Mesh(mode="triangle"), texture="grass")

        for key, value in kwargs.items():
            setattr(self, key, value)

    def generate_chunk(self):
        self.model.vertices, self.model.uvs = [], []

        for entity_pos, entity in self.entities.items():
            entity_pos = [float(i) for i in entity_pos.split()]
            model = self.game.entity_dict[entity["name"]]
            if model == None:
                continue

            self.model.uvs.extend(model["uvs"])
            self.model.normals.extend(model["normals"])
            self.model.vertices.extend([(vertex[0] + entity_pos[0],
                                         vertex[1] + entity_pos[1],
                                         vertex[2] + entity_pos[2])
                                         for vertex in model["vertices"]])

        self.model.generate()
