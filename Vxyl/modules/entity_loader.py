import os
import json
import numpy as np

from panda3d.core import Texture as PandaTexture, PNMImage, SamplerState

from cython_functions import WorldGenerator, GameEntity


class EntityLoader():

    def __init__(self):
        texture_index = 0
        entities = []
        self.entity_data = []
        self.entity_index = {}

        files = os.listdir("./data/entities/")
        files.sort()

        for file_name in files:
            with open(f"./data/entities/{file_name}") as file:
                data = json.load(file)
                entities.append(data)

        self.texture_array = PandaTexture()
        self.texture_array.setup_2d_texture_array(sum([len(entity["textures"]) for entity in entities]))
        self.texture_array.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.texture_array.set_magfilter(SamplerState.FT_nearest)
        self.texture_array.set_anisotropic_degree(16)

        for i, entity in enumerate(entities):
            if not entity["name"]:
                continue

            self.entity_index[entity["name"]] = i

            texture_names = entity["textures"]
            model_name = entity["model"]
            collider = entity["collider"]

            game_entity = GameEntity()
            game_entity.transparent = bool(entity["transparent"])
            game_entity.collision = bool(entity["collision"])

            if texture_names:
                texture_names.reverse()
                for texture_name in texture_names:
                    texture = PNMImage()   
                    texture.read(f"./assets/textures/{texture_name}.png")
                    self.texture_array.load(texture, z=texture_index, n=0)
                    texture_index += 1

            vertices = []
            uvs = []
            if model_name:
                with open(f"./assets/models/{model_name}.json") as file:
                    model = json.load(file)

                vertices = model["vertices"]
                uvs = [[uv[0], uv[1], texture_index - uv[2] - 1] for uv in model["uvs"]]

                game_entity.shape = len(vertices)

            game_entity.vertices = np.array(vertices, dtype=np.single).ravel()
            game_entity.uvs = np.array(uvs, dtype=np.single).ravel()

            game_entity.collider = np.array(collider, dtype=np.single)

            self.entity_data.append(game_entity)

        # print(self.entity_index)

        self.world_generator = WorldGenerator(np.array(self.entity_data))