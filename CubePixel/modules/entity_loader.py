import os
import json
import numpy as np

from ursina.mesh_importer import load_model


def load_entities():
    entity_data = {}
    dirs = os.listdir("data/entities/")

    for dir in dirs:
        with open(f"data/entities/{dir}", "r") as f:
            data = json.load(f)
            model = load_model(data["model"], use_deepcopy=True)
            if model:
                entity_data[data["name"]] = {
                    "vertices": np.array(model.vertices),
                    "uvs": np.array(model.uvs),
                    "normals": np.array(model.normals)
                }
            else:
                entity_data[data["name"]] = None

    return entity_data


entity_data = load_entities()
