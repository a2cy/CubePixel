import os
import json
import numpy as np

from ursina import Shader

from panda3d.core import Texture as PandaTexture, PNMImage, SamplerState

from cython_functions import VoxelType


class ResourceLoader():

    def __init__(self):
        self.load_shaders()

        self.load_voxel_data()


    def load_shaders(self):
        self.voxel_shader = Shader.load(language=Shader.GLSL,
                                        vertex="./res/shaders/voxel.vert",
                                        fragment="./res/shaders/voxel.frag",)


    def load_voxel_data(self):
        texture_index = 0
        voxels = []

        files = os.listdir("./res/entities/")
        files.sort()

        for file_name in files:
            with open(f"./res/entities/{file_name}") as file:
                data = json.load(file)
                voxels.append(data)

        self.texture_array = PandaTexture()
        self.texture_array.setup_2d_texture_array(sum([len(voxel["textures"]) for voxel in voxels]))
        self.texture_array.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.texture_array.set_magfilter(SamplerState.FT_nearest)
        self.texture_array.set_anisotropic_degree(16)

        self.voxel_types = []
        self.voxel_index = {}

        for i, voxel in enumerate(voxels):
            self.voxel_index[voxel["name"]] = i

            texture_names = voxel["textures"]
            model_name = voxel["model"]

            if texture_names:
                texture_names.reverse()
                for texture_name in texture_names:
                    texture = PNMImage()   
                    texture.read(f"./res/textures/{texture_name}.png")
                    self.texture_array.load(texture, z=texture_index, n=0)
                    texture_index += 1

            vertices = []
            uvs = []
            if model_name:
                with open(f"./res/models/{model_name}.json") as file:
                    model = json.load(file)

                vertices = model["vertices"]
                uvs = [[uv[0], uv[1], texture_index - uv[2] - 1] for uv in model["uvs"]]

            voxel_type = VoxelType()
            voxel_type.shape = len(vertices)
            voxel_type.vertices = np.array(vertices, dtype=np.single).ravel()
            voxel_type.uvs = np.array(uvs, dtype=np.single).ravel()
            voxel_type.occlusion = bool(voxel["occlusion"])
            voxel_type.collision = bool(voxel["collision"])

            self.voxel_types.append(voxel_type)

instance = ResourceLoader()

# print(instance.voxel_index)