import json
import os

from direct.stdpy import threading
from perlin_noise import PerlinNoise
from ursina import *

from modules.entity_model_loader import instance as entity_model_loader


class TerrainMesh(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game

        self.seed = 2021
        self.render_distance = 4
        self.chunk_with = 15

        os.makedirs("saves/", exist_ok=True)

        self.noise = PerlinNoise(octaves=2, seed=self.seed)
        self.amp = 16
        self.freq = 64

        self.chunk_dict = {}
        self.player_chunk = ()
        self.updating = False

    def unload(self):
        self.updating = False
        self.update_thread.join()

    def update(self):
        player = self.game.player

        new_player_chunk = (
            int(round_to_closest(player.position[0], self.chunk_with)),
            int(round_to_closest(player.position[1], self.chunk_with)),
            int(round_to_closest(player.position[2], self.chunk_with)))

        if self.player_chunk != new_player_chunk and not self.updating:
            self.updating = True
            self.player_chunk = new_player_chunk
            self.update_thread = threading.Thread(
                target=self.updateChunks, args=[])
            self.update_thread.start()

    def updateChunks(self):
        new_chunk_ids = []

        for x in range(-self.render_distance, self.render_distance+1):
            for z in range(-self.render_distance, self.render_distance+1):
                for y in range(-self.render_distance, self.render_distance+1):
                    new_chunk_ids.append((x*self.chunk_with+self.player_chunk[0],
                                          y*self.chunk_with +
                                          self.player_chunk[1],
                                          z*self.chunk_with+self.player_chunk[2]))

        for chunk_id in self.chunk_dict.copy():
            if chunk_id not in new_chunk_ids:
                destroy(self.chunk_dict.pop(chunk_id))
                time.sleep(.02)

        for chunk_id in new_chunk_ids:
            if not self.updating:
                return

            if not chunk_id in self.chunk_dict:
                filename = f"saves/{chunk_id}.json"

                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        entities = eval(json.load(f)["entities"])

                    chunk = Chunk(self, parent=self)
                    chunk.position = chunk_id
                    chunk.entities = entities
                    chunk.generateChunk()
                    self.chunk_dict[chunk_id] = chunk

                else:
                    chunk = Chunk(self, parent=self)
                    chunk.position = chunk_id
                    chunk.entities = self.getChunkentities(chunk_id)
                    chunk.generateChunk()
                    self.chunk_dict[chunk_id] = chunk

                    with open(filename, 'w+') as f:
                        json.dump({"entities": f"{chunk.entities}"}, f)

        self.updating = False

    def getChunkentities(self, pos):
        entities = {}
        for i in range(self.chunk_with**3):
            x = i//self.chunk_with//self.chunk_with
            y = i//self.chunk_with % self.chunk_with
            z = i % self.chunk_with % self.chunk_with
            max_y = int(self.noise([(x+pos[0])/self.freq,
                                    (z+pos[2])/self.freq])*
                                    self.amp+self.amp/2)

            if y+pos[1] <= max_y:
                entities[(x, y, z)] = {'name': 'grass',
                                       'rotation': Vec3(0, 0, 0)}

            else:
                entities[(x, y, z)] = {'name': 'air',
                                       'rotation': Vec3(0, 0, 0)}

        return entities


class Chunk(Entity):
    def __init__(self, terrain_mesh, **kwargs):
        self.chunk_with = terrain_mesh.chunk_with-1
        self.entities = {}
        super().__init__(
            model=Mesh(mode='triangle', thickness=.05, static=False),
            texture='grass',
            scale=1,
            **kwargs)

    def generateChunk(self):
        self.model.vertices = []
        self.model.uvs = []
        self.model.normals = []

        for entity_pos, entity in self.entities.items():
            model = entity_model_loader.entity_model_dict[entity['name']]
            if model == None:
                continue

            self.model.uvs.extend(model.uvs)
            self.model.normals.extend(model.normals)
            for vertex in model.vertices:
                self.model.vertices.append((vertex[0]+entity_pos[0],
                                            vertex[1]+entity_pos[1],
                                            vertex[2]+entity_pos[2]))

        self.model.generate()
