import os
import json
from ursina import *


class ModelLoader():
    def __init__(self):
        self.entity_model_dict = {}
        dirs = os.listdir('data/entities/')

        for dir in dirs:

            with open(f'data/entities/{dir}', 'r') as f:
                data = json.load(f)
                self.entity_model_dict[data['name']] = load_model(
                    data['model'], use_deepcopy=True)

                if self.entity_model_dict[data['name']] != None and len(self.entity_model_dict[data['name']].triangles) < 1:
                    self.entity_model_dict[data['name']].triangles = [
                        i for i in range(len(self.entity_model_dict[data['name']].vertices))]


instance = ModelLoader()
