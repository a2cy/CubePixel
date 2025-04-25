import os
import json

from ursina import print_warning

from panda3d.core import Texture, PNMImage, SamplerState, Shader

from cython_functions import VoxelType


class ResourceLoader:

    def __init__(self):
        self.voxel_shader = Shader.load(Shader.SL_GLSL, "./shaders/voxel.vert", "./shaders/voxel.frag",)
        self.voxel_display_shader = Shader.load(Shader.SL_GLSL, "./shaders/voxel_display.vert", "./shaders/voxel_display.frag",)
        self.selector_shader = Shader.load(Shader.SL_GLSL, "./shaders/selector.vert", "./shaders/selector.frag",)

        files = os.listdir("./res/voxels/")

        voxels = []
        loaded_textures = []
        self.voxel_types = []

        for file_name in files:
            if not file_name.endswith(".json"):
                continue

            with open(f"./res/voxels/{file_name}") as file:
                data = json.load(file)
                result = self.validate_type(data)

                if result:
                    print_warning(f"failed to load voxel type \'{file_name}\' ({result})")
                    continue

                if data["index"] == 0:
                    continue

                voxels.append(data)

        voxels.sort(key=lambda value: value["index"])

        for voxel in voxels:
            texture_names = voxel["textures"]
            voxel_type = VoxelType()

            for texture_name in texture_names:
                if not texture_name in loaded_textures:
                    loaded_textures.append(texture_name)

            if len(texture_names) == 1:
                voxel_type.up = loaded_textures.index(texture_names[0])
                voxel_type.down = loaded_textures.index(texture_names[0])
                voxel_type.side = loaded_textures.index(texture_names[0])

            elif len(texture_names) == 3:
                voxel_type.up = loaded_textures.index(texture_names[0])
                voxel_type.down = loaded_textures.index(texture_names[1])
                voxel_type.side = loaded_textures.index(texture_names[2])

            voxel_type.occlusion = bool(voxel["occlusion"])
            voxel_type.collision = bool(voxel["collision"])
            voxel_type.inventory = bool(voxel["inventory"])

            self.voxel_types.append(voxel_type)

        self.texture_array = Texture()
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
                print_warning(f"failed to load texture \'{texture_name}\' (wrong format)")


    def validate_type(self, type: dict):
        keys = {"index": int, "textures": list, "occlusion": bool, "collision": bool, "inventory": bool}
        texture_names = type["textures"]

        for key, value in keys.items():
            if not key in type.keys():
                return f"missing key \'{key}\'"

            if not isinstance(type[key], value):
                return f"key \'{key}\' has wrong type"

        if not len(texture_names) in (1, 3):
            return "wrong texture definition"

        for texture_name in texture_names:
            if not os.path.isfile(f"./res/textures/{texture_name}.png"):
                return f"missing texture \'{texture_name}\'"


instance = ResourceLoader()