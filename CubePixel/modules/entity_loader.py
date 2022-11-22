import os
import json
import numpy as np

from ursina.mesh_importer import load_model


def load_entities():
    entity_data = {}
    entity_index = {}

    for i, file in enumerate(os.listdir("data/entities/")):
        with open(f"data/entities/{file}", "r") as file:
            data = json.load(file)
            entity_index[data["name"]] = i

            if not data["model"] == "None":
                model = load_model(data["model"])

                entity_data[i] = {"vertices": np.array(model.vertices, dtype=np.float32),
                                  "uvs": np.array(model.uvs, dtype=np.float32),
                                  "normals": np.array(model.normals, dtype=np.float32)}
            else:
                entity_data[i] = None

    return (entity_data, entity_index)


entity_data, entity_index = load_entities()
