import json
import os

from direct.stdpy import threading
from opensimplex import OpenSimplex
from ursina import *

from modules.model_loader import instance as model_loader


class ChunkHandler(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.settings = self.game.settings

    def load_world(self, world):
        self.seed = 2021
        self.render_distance = self.settings.settings.render_distance

        self.world_path = f'saves/{world}/'
        os.makedirs(f'{self.world_path}chunks/', exist_ok=True)

        self.noise = OpenSimplex(seed=self.seed).noise2
        self.amp = self.settings.world.amp
        self.freq = self.amp*self.settings.world.amp_multiplier
        self.chunk_with = self.settings.world.chunk_with

        self.chunk_dict = {}
        self.player_chunk = ()
        self.updating = False

    def unload_world(self):
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
                target=self.update_chunks, args=[])
            self.update_thread.start()

    def update_chunks(self):
        new_chunk_ids = []

        world_with = self.render_distance*2+1
        for i in range(world_with**3):
            x = i//world_with//world_with-(world_with-1)/2
            y = i//world_with % world_with-(world_with-1)/2
            z = i % world_with % world_with-(world_with-1)/2

            new_chunk_ids.append((int(x*self.chunk_with+self.player_chunk[0]),
                                  int(y*self.chunk_with+self.player_chunk[1]),
                                  int(z*self.chunk_with+self.player_chunk[2])))

        for chunk_id in self.chunk_dict.copy():
            if chunk_id not in new_chunk_ids:
                destroy(self.chunk_dict.pop(chunk_id))
                print(f'Unloaded chunk {chunk_id}')
                time.sleep(.02)

        for chunk_id in new_chunk_ids:
            if not self.updating:
                return

            if not chunk_id in self.chunk_dict:
                filename = f"{self.world_path}chunks/{chunk_id}.json"

                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        entities = eval(json.load(f)["entities"])

                    chunk = Chunk(parent=self, position=chunk_id)
                    chunk.entities = entities
                    chunk.generate_chunk()
                    self.chunk_dict[chunk_id] = chunk

                else:
                    chunk = Chunk(parent=self, position=chunk_id)
                    chunk.entities = self.get_chunkentities(chunk_id)
                    chunk.generate_chunk()
                    self.chunk_dict[chunk_id] = chunk

                    with open(filename, 'w+') as f:
                        json.dump({"entities": f"{chunk.entities}"}, f)

            print(f'Loaded chunk {chunk_id}')
            time.sleep(.02)

        self.updating = False

    def get_chunkentities(self, pos):
        entities = {}
        for i in range(self.chunk_with**3):
            x = i//self.chunk_with//self.chunk_with-(self.chunk_with-1)/2
            y = i//self.chunk_with % self.chunk_with-(self.chunk_with-1)/2
            z = i % self.chunk_with % self.chunk_with-(self.chunk_with-1)/2

            max_y = int(self.noise((x+pos[0])/self.freq,
                                   (z+pos[2])/self.freq)*self.amp+self.amp/2)

            if y+pos[1] <= max_y:
                entities[(x, y, z)] = {'name': 'grass',
                                       'rotation': Vec3(0, 0, 0)}

            else:
                entities[(x, y, z)] = {'name': 'air',
                                       'rotation': Vec3(0, 0, 0)}

        return entities


class Chunk(Entity):
    def __init__(self, **kwargs):
        self.entities = {}
        super().__init__(
            model=Mesh(mode='triangle'),
            texture='grass',
            **kwargs)

    def generate_chunk(self):
        self.model.vertices, self.model.uvs = [], []

        for entity_pos, entity in self.entities.items():
            model = model_loader.entity_model_dict[entity['name']]
            if model == None:
                continue

            self.model.uvs.extend(model.uvs)
            self.model.vertices.extend([(vertex[0]+entity_pos[0],
                                         vertex[1]+entity_pos[1],
                                         vertex[2]+entity_pos[2])
                                        for vertex in model.vertices])

        self.model.generate()
