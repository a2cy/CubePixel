import json
import os
import ursina
import opensimplex
import direct.stdpy

import numpy as np

from modules.chunk_mesh import ChunkMesh
from modules.texture_shader import texture_shader
from cython_functions import generate_chunkentities, combine_mesh


class ChunkHandler(ursina.Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game

        self.amp = self.game.parameters["amp"]
        self.freq = self.game.parameters["freq"]
        self.chunk_with = self.game.parameters["chunk_with"]
        self.render_distance = self.game.settings["render_distance"]

        self.chunk_dict = {}
        self.player_chunk = []
        self.update_percentage = 0
        self.updating = False
        self.world_loaded = False

        os.makedirs(f"./saves/", exist_ok=True)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def create_world(self, world_name, seed):
        world_path = f"./saves/{world_name}/"
        
        os.makedirs(f"{world_path}chunks/", exist_ok=True)
        self.world_data = {"name": world_name, "seed": seed, "player_position": "0 0 0"}

        with open(f"{world_path}data.json", "w+") as file:
            json.dump(self.world_data, file, indent=4)

        self.load_world(world_name)


    def load_world(self, world_name):
        self.world_path = f"./saves/{world_name}/"

        with open(f"{self.world_path}data.json") as file:
            self.world_data = json.load(file)

        player_position = self.world_data["player_position"].split()

        self.game.player.position = [float(i) for i in player_position]

        self.noise = opensimplex.OpenSimplex(self.world_data["seed"]).noise2

        self.world_loaded = True


    def unload_world(self):
        self.world_loaded = False
        self.update_percentage = 0
        self.updating = False
        self.update_thread.join()
        self.player_chunk = []

        with open(f"{self.world_path}data.json", "w+") as file:
            player_position = self.game.player.position

            self.world_data["player_position"] = f"{player_position[0]} {player_position[1]} {player_position[2]}"

            json.dump(self.world_data, file, indent=4)

        for chunk_id in self.chunk_dict.copy():
            ursina.destroy(self.chunk_dict.pop(chunk_id))


    def update_chunks(self):
        self.update_percentage = 0
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
                ursina.destroy(self.chunk_dict.pop(chunk_id))

                ursina.time.sleep(.002)

        for i, chunk_id in enumerate(new_chunk_ids):
            if not self.updating:
                return

            if not chunk_id in self.chunk_dict:
                filename = f"{self.world_path}chunks/{chunk_id}.npy"

                if os.path.exists(filename):
                    entities = np.load(filename)

                else:
                    entities = generate_chunkentities(self.chunk_with, self.noise, self.amp, self.freq, chunk_id, self.game.entity_index)

                    np.save(filename, entities)

                vertices, uvs, normals = combine_mesh(self.game.entity_data, entities)

                chunk = ursina.Entity(parent=self, position=chunk_id, model=ChunkMesh(vertices.ravel(), uvs.ravel(), normals.ravel()), shader=texture_shader)
                chunk.set_shader_input("texture_array", self.game.texture_array)

                self.chunk_dict[chunk_id] = chunk

            self.update_percentage += 100/len(new_chunk_ids)

        self.updating = False

        if self.game.profile_mode:
            ursina.application.quit()


    def update(self):
        player = self.game.player

        new_player_chunk = [int(ursina.round_to_closest(player.position[0], self.chunk_with)),
                            int(ursina.round_to_closest(player.position[1], self.chunk_with)),
                            int(ursina.round_to_closest(player.position[2], self.chunk_with))]

        if self.player_chunk != new_player_chunk and not self.updating and self.world_loaded:
            self.updating = True
            self.player_chunk = new_player_chunk
            self.update_thread = direct.stdpy.threading.Thread(target=self.update_chunks, args=[])
            self.update_thread.start()
