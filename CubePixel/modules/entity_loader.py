import os
import json
import numpy as np

from PIL import Image
from ursina import load_model


def load_entities():
    entity_data = {}
    entity_index = {}

    entities = []
    for file_name in os.listdir("./data/entities/"):
        with open(f"./data/entities/{file_name}", "r") as file:
            data = json.load(file)
            entities.append(data)

    loaded_textures = {}
    atlas_size = [0, 0]
    for entity in entities:
        if not entity["texture"] == "None":
            texture_name = entity["texture"]
            texture = Image.open(f"./assets/textures/{texture_name}.png")
            texture = texture.convert("RGBA")
            texture = np.asarray(texture)
            loaded_textures[entity["texture"]] = texture

            atlas_size[0] = texture.shape[1] if texture.shape[1] > atlas_size[0] else atlas_size[0]
            atlas_size[1] += texture.shape[0]

    texture_atlas = np.zeros((atlas_size[0], atlas_size[1], 4), dtype=np.uint8)

    texture_data = {}
    slice_index = 0
    for i, texture in loaded_textures.items():
        new_slice_index = slice_index + texture.shape[0]

        texture_atlas[:,slice_index:new_slice_index] = texture

        texture_data[i] = {"size" : np.array([atlas_size[1]/texture.shape[1], atlas_size[0]/texture.shape[0]]), "position" : np.array([slice_index/atlas_size[1]+atlas_size[1]/texture.shape[1], 0])}
    
        slice_index = new_slice_index

    texture = Image.fromarray(texture_atlas)
    texture.save("texture_atlas.png")

    for i, entity in enumerate(entities):
        entity_index[entity["name"]] = i
        if not entity["model"] == "None":
            model = load_model(entity["model"], use_deepcopy=True)

            uvs = np.array(model.uvs)
            uvs /= texture_data[entity["texture"]]["size"]
            uvs += texture_data[entity["texture"]]["position"]

            entity_data[i] = {"vertices": np.array(model.vertices, dtype=np.float32),
                              "uvs": np.array(uvs, dtype=np.float32),
                              "normals": np.array(model.normals, dtype=np.float32)}
        else:
            entity_data[i] = None

    return (entity_data, entity_index)


entity_data, entity_index = load_entities()
