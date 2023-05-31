import os
import json
import numpy as np

from ursina import load_model
from panda3d.core import Texture as PandaTexture, PNMImage, SamplerState

from cython_functions import WordGenerator


class GameEntity:
    shape = 0
    vertices = None
    uvs = None
    transparent = False
    solid = True


def load_entities():
    entity_data = []
    entity_index = []

    files = os.listdir("./data/entities/")
    files.sort()

    entities = []
    for file_name in files:
        with open(f"./data/entities/{file_name}", "r") as file:
            data = json.load(file)
            entities.append(data)

    texture_array = PandaTexture()
    texture_array.setup2dTextureArray(len([0 for entity in entities if not entity["texture"] == "None"]))
    texture_array.setMagfilter(SamplerState.FT_nearest)

    texture_index = 0
    for entity in entities:
        entity_index.append(entity["name"])

        texture_name = entity["texture"]
        model_name = entity["model"]

        game_entity = GameEntity()
        game_entity.transparent = bool(entity["transparent"])
        game_entity.solid = bool(entity["solid"])

        if not texture_name == "None":
            texture = PNMImage()   
            texture.read(f"./assets/textures/{texture_name}.png")
            texture_array.load(texture, z=texture_index, n=0)
            texture_index += 1

        if not model_name == "None":
            model = load_model(name=model_name, use_deepcopy=True)

            uvs = [[uv[0], uv[1], texture_index-1] for uv in model.uvs]

            game_entity.vertices = np.asarray(model.vertices, dtype=np.single)
            game_entity.uvs = np.asarray(uvs, dtype=np.single)

            game_entity.shape = game_entity.vertices.shape[0]

        entity_data.append(game_entity)

        world_generator = WordGenerator(np.asarray(entity_data))

    return (world_generator, texture_array)


world_generator, texture_array = load_entities()