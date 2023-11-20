import os
import json
import numpy as np

from panda3d.core import Texture as PandaTexture, PNMImage, SamplerState

from cython_functions import WorldGenerator, PyGameEntity


def load_entities():
    texture_index = 0
    entities = []
    entity_data = []

    files = os.listdir("./data/entities/")
    files.sort()

    for file_name in files:
        with open(f"./data/entities/{file_name}") as file:
            data = json.load(file)
            entities.append(data)

    texture_array = PandaTexture()
    texture_array.setup2dTextureArray(sum([len(entity["textures"]) for entity in entities]))
    texture_array.setMinfilter(SamplerState.FT_linear_mipmap_linear)
    texture_array.setMagfilter(SamplerState.FT_nearest)
    texture_array.setAnisotropicDegree(16)

    for entity in entities:
        if not entity["name"]:
            continue

        textures = entity["textures"]
        model_name = entity["model"]

        game_entity = PyGameEntity()
        game_entity.transparent = bool(entity["transparent"])
        game_entity.solid = bool(entity["solid"])

        if textures:
            textures.reverse()
            for texture_name in textures:
                texture = PNMImage()   
                texture.read(f"./assets/textures/{texture_name}.png")
                texture_array.load(texture, z=texture_index, n=0)
                texture_index += 1

        vertices = []
        uvs = []
        if model_name:
            with open(f"./assets/models/{model_name}.json") as file:
                model = json.load(file)

            vertices = model["vertices"]
            uvs = [[uv[0], uv[1], texture_index - uv[2] - 1] for uv in model["uvs"]]

            game_entity.shape = len(vertices)

        vertices = np.array(vertices, dtype=np.single).ravel()
        uvs = np.array(uvs, dtype=np.single).ravel()

        game_entity.vertices = np.array(vertices, dtype=np.single).ravel()
        game_entity.uvs = np.array(uvs, dtype=np.single).ravel()

        entity_data.append(game_entity)

    world_generator = WorldGenerator(np.array(entity_data))

    return [world_generator, texture_array]


world_generator, texture_array = load_entities()