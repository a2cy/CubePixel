import os
import json
from ursina import *


def load_entities():
    entity_dict = {}
    dirs = os.listdir('data/entities/')

    for dir in dirs:
        with open(f'data/entities/{dir}', 'r') as f:
            data = json.load(f)
            model = load_model(data['model'], use_deepcopy=True)
            if model:
                entity_dict[data['name']] = {
                    'vertices': model.vertices, 'uvs': model.uvs}
            else:
                entity_dict[data['name']] = None

    return entity_dict


entity_dict = load_entities()
