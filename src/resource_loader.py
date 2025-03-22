import os
import json

from ursina import print_info

from panda3d.core import Texture as PandaTexture, PNMImage, SamplerState, Shader as Shader

from cython_functions import VoxelType


class ResourceLoader:

    def __init__(self):
        self.voxel_shader = Shader.load(Shader.SL_GLSL, "./shaders/voxel.vert", "./shaders/voxel.frag",)
        self.selector_shader = Shader.load(Shader.SL_GLSL, "./shaders/selector.vert", "./shaders/selector.frag",)

        files = os.listdir("./res/entities/")
        files.sort()

        voxels = []
        for file_name in files:
            with open(f"./res/entities/{file_name}") as file:
                data = json.load(file)
                voxels.append(data)

        loaded_textures = []

        for voxel in voxels:
            textures = voxel["textures"]

            for texture_name in textures:
                if not os.path.isfile(f"./res/textures/{texture_name}.png"):
                    print_info(f"failed to load texture: {texture_name} (file missing)")
                    continue

                if not texture_name in loaded_textures:
                    loaded_textures.append(texture_name)

        self.texture_array = PandaTexture()
        self.texture_array.setup_2d_texture_array(len(loaded_textures))
        self.texture_array.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.texture_array.set_magfilter(SamplerState.FT_nearest)
        self.texture_array.set_anisotropic_degree(16)

        for i, texture_name in enumerate(loaded_textures):
            try:
                texture = PNMImage()
                texture.read(f"./res/textures/{texture_name}.png")
                self.texture_array.load(texture, z=i, n=0)
            except:
                print_info(f"failed to load texture: {texture_name} (wrong format)")

        self.voxel_types = []
        self.voxel_index = {}

        for i, voxel in enumerate(voxels):
            self.voxel_index[voxel["name"]] = i + 1

            texture_names = voxel["textures"]

            voxel_type = VoxelType()

            if len(texture_names) == 0:
                pass

            elif len(texture_names) == 1:
                voxel_type.up = loaded_textures.index(texture_names[0])
                voxel_type.down = loaded_textures.index(texture_names[0])
                voxel_type.side = loaded_textures.index(texture_names[0])

            elif len(texture_names) == 3:
                voxel_type.up = loaded_textures.index(texture_names[0])
                voxel_type.down = loaded_textures.index(texture_names[1])
                voxel_type.side = loaded_textures.index(texture_names[2])

            else:
                print_info(f"failed to load voxel: {voxel["name"]} (wrong texture definition)")
                continue

            voxel_type.occlusion = bool(voxel["occlusion"])
            voxel_type.collision = bool(voxel["collision"])
            voxel_type.inventory = bool(voxel["inventory"])

            self.voxel_types.append(voxel_type)


instance = ResourceLoader()

# print(instance.voxel_index)
