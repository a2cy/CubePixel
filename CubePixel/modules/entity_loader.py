import os
import json
import numpy as np

from ursina import *


def load_entities():
    entity_dict = {}
    dirs = os.listdir("data/entities/")

    for dir in dirs:
        with open(f"data/entities/{dir}", "r") as f:
            data = json.load(f)
            model = load_model(data["model"], use_deepcopy=True)
            if model:
                entity_dict[data["name"]] = {
                    "vertices": np.array(model.vertices),
                    "uvs": np.array(model.uvs),
                    "normals": np.array(model.normals)
                }
            else:
                entity_dict[data["name"]] = None

    return entity_dict


entity_dict = load_entities()
