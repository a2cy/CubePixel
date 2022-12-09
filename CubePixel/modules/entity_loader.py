import os
import json
import numpy as np

from panda3d.core import Texture as PandaTexture, PNMImage, SamplerState
from ursina import load_model


def load_entities():
    entity_data = []
    entity_index = {}

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
    for i, entity in enumerate(entities):
        entity_index[entity["name"]] = i

        texture_name = entity["texture"]
        model_name = entity["model"]
        if not texture_name == "None":
            texture = PNMImage()   
            texture.read(f"./assets/textures/{texture_name}.png")
            texture_array.load(texture, z=texture_index, n=0)
            texture_index += 1

        if not model_name == "None":
            model = load_model(name=model_name, use_deepcopy=True)

            uvs = [[uv[0], uv[1], texture_index-1] for uv in model.uvs]

            entity_data.insert(i, [np.array(model.vertices, dtype=np.float32), np.array(uvs, dtype=np.float32), np.array(model.normals, dtype=np.float32)])
        else:
            entity_data.insert(i, None)

    return (entity_data, entity_index, texture_array)


entity_data, entity_index, texture_array = load_entities()
