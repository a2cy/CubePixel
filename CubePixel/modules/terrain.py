import os

from direct.stdpy import thread
from perlin_noise import PerlinNoise
from ursina import *


class TerrainMesh(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game

        self.seed = 2021
        self.render_distance = 2
        self.chunk_with = 15

        os.makedirs("saves/", exist_ok=True)

        self.noise = PerlinNoise(octaves=2, seed=self.seed)
        self.amp = 16
        self.freq = 64

        self.chunk_dict = {}
        self.player_chunk = ()
        self.updating = False

    def update(self):
        player = self.game.player

        new_player_chunk = (
            int(round_to_closest(player.position[0], self.chunk_with)),
            int(round_to_closest(player.position[1], self.chunk_with)),
            int(round_to_closest(player.position[2], self.chunk_with)))

        if self.player_chunk != new_player_chunk and not self.updating:
            self.updating = True
            self.player_chunk = new_player_chunk
            thread.start_new_thread(function=self.updateChunks, args=[])

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
            if not chunk_id in self.chunk_dict:
                filename = "saves/"+f"{chunk_id}.txt"

                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        entities = eval(f.read())

                    chunk = Chunk(self)
                    chunk.position = chunk_id
                    chunk.entities = entities
                    chunk.generateChunk()
                    self.chunk_dict[chunk_id] = chunk

                else:
                    chunk = Chunk(self)
                    chunk.position = chunk_id
                    chunk.entities = self.getChunkentities(chunk_id)
                    chunk.generateChunk()
                    self.chunk_dict[chunk_id] = chunk

                    with open(filename, 'w+') as f:
                        f.write(f"{chunk.entities}")

        self.updating = False

    def getChunkentities(self, pos):
        entities = {}
        for i in range(self.chunk_with**3):
            x = i//self.chunk_with//self.chunk_with
            y = i//self.chunk_with % self.chunk_with
            z = i % self.chunk_with % self.chunk_with
            max_y = int(self.noise([(x+pos[0])/self.freq,
                                    (z+pos[2])/self.freq])*self.amp)

            if y+pos[1] <= max_y:
                entities[(x, y, z)] = ('grass', Vec3(0, 0, 0))

        return entities


class Chunk(Entity):
    def __init__(self, terrain_mesh, **kwargs):
        self.chunk_with = terrain_mesh.chunk_with-1
        super().__init__(
            model=Mesh(mode='triangle', thickness=.05, static=False),
            texture='grass',
            origin=(self.chunk_with/2, self.chunk_with/2, self.chunk_with/2),
            scale=1,
            **kwargs)

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        self._entities = value

    def generateChunk(self):
        model = load_model('cube', use_deepcopy=True)
        self.model.vertices = []
        self.model.uvs = []
        self.model.normals = []

        for entity in self.entities:
            self.model.uvs.extend(model.uvs)
            self.model.normals.extend(model.normals)

            for vert in model.vertices:
                self.model.vertices.append(
                    (vert[0] + entity[0], vert[1] + entity[1], vert[2] + entity[2]))

        self.model.generate()
