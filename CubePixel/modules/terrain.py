from direct.stdpy import thread
from perlin_noise import PerlinNoise
from ursina import *


class TerrainMesh(Entity):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.noise = PerlinNoise(octaves=2, seed=2021)
        self.amp = 16
        self.freq = 64

        self.chunk_distance = 1
        self.terrain_with = self.chunk_distance*2 + 1
        self.chunk_with = 15
        self.chunk_dict = {}

        self.player_chunk = ()
        self.collision_with = 1

        for i in range(self.terrain_with**3):
            chunk = Chunk(self)
            self.chunk_dict[i] = chunk

    def update(self):
        current_player_chunk = (
            int(round_to_closest(self.game.player.position[0], self.chunk_with)),
            int(round_to_closest(self.game.player.position[1], self.chunk_with)),
            int(round_to_closest(self.game.player.position[2], self.chunk_with)))
        if not self.player_chunk == current_player_chunk:
            self.player_chunk = current_player_chunk
            thread.start_new_thread(function=self.updateChunks, args=[])

    def updateChunks(self):
        temp_chunk_dict = {}

        for i, chunk in enumerate(self.chunk_dict):
            chunk_pos = (
                i//self.terrain_with//self.terrain_with * self.chunk_with -
                ((self.terrain_with-1)/2 * self.chunk_with) +
                self.player_chunk[0],

                i//self.terrain_with % self.terrain_with * self.chunk_with -
                ((self.terrain_with-1)/2 * self.chunk_with) +
                self.player_chunk[1],

                i % self.terrain_with % self.terrain_with * self.chunk_with -
                ((self.terrain_with-1)/2 * self.chunk_with) + self.player_chunk[2])

            self.chunk_dict[chunk].entities = self.getChunkentities(chunk_pos)
            self.chunk_dict[chunk].position = chunk_pos
            self.chunk_dict[chunk].generateChunk()

            temp_chunk_dict[chunk_pos] = self.chunk_dict[chunk]

        self.chunk_dict = temp_chunk_dict

    def getChunkentities(self, pos):
        entities = {}
        for i in range(self.chunk_with**3):
            x = i//self.chunk_with//self.chunk_with
            y = i//self.chunk_with % self.chunk_with
            z = i % self.chunk_with % self.chunk_with
            max_y = int(self.noise(
                [(x+pos[0])/self.freq, (z+pos[2])/self.freq])*self.amp)
            if y+pos[1] <= max_y:
                entities[(x, y, z)] = ('grass', Vec3(0, 0, 0))

        return entities


class Chunk(Entity):
    def __init__(self, terrain_mesh):
        self.chunk_with = terrain_mesh.chunk_with-1
        super().__init__(
            model=Mesh(mode='triangle', thickness=.05, static=False),
            texture='white_cube',
            origin=(self.chunk_with/2, self.chunk_with/2, self.chunk_with/2),
            scale=1)

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
        #self.collider = 'mesh'
