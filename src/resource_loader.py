import os
import json
import numpy as np

from ursina import print_warning

from panda3d.core import Texture, PNMImage, SamplerState, Shader


class ResourceLoader:
    def __init__(self) -> None:
        self.voxel_shader = Shader.load(Shader.SL_GLSL, "./shaders/voxel.vert", "./shaders/voxel.frag")
        self.voxel_display_shader = Shader.load(Shader.SL_GLSL, "./shaders/voxel_display.vert", "./shaders/voxel_display.frag")
        self.outline_shader = Shader.load(Shader.SL_GLSL, "./shaders/outline.vert", "./shaders/outline.frag")

        files = os.listdir("./assets/voxel_types/")

        voxels = []
        loaded_textures = []

        for file_name in files:
            if not file_name.endswith(".json"):
                continue

            with open(f"./assets/voxel_types/{file_name}") as file:
                data = json.load(file)
                result = self.validate_type(data)

                if result:
                    print_warning(f"failed to load voxel type '{file_name}' ({result})")
                    continue

                voxels.append(data)

        voxels.sort(key=lambda value: value["index"])
        self.type_count = len(voxels)

        self.texture_types = np.zeros(self.type_count * 3, dtype=np.intc)
        self.collision_types = np.zeros(self.type_count, dtype=np.intc)
        self.occlusion_types = np.zeros(self.type_count, dtype=np.intc)

        for i, voxel in enumerate(voxels):
            texture_names = voxel["textures"]

            for texture_name in texture_names:
                if texture_name not in loaded_textures:
                    loaded_textures.append(texture_name)

            if len(texture_names) == 1:
                self.texture_types[i * 3 + 0] = loaded_textures.index(texture_names[0])
                self.texture_types[i * 3 + 1] = loaded_textures.index(texture_names[0])
                self.texture_types[i * 3 + 2] = loaded_textures.index(texture_names[0])

            elif len(texture_names) == 3:
                self.texture_types[i * 3 + 0] = loaded_textures.index(texture_names[0])
                self.texture_types[i * 3 + 1] = loaded_textures.index(texture_names[1])
                self.texture_types[i * 3 + 2] = loaded_textures.index(texture_names[2])

            self.collision_types[i] = voxel["collision"]
            self.occlusion_types[i] = voxel["occlusion"]

        self.texture_array = Texture()
        self.texture_array.setup_2d_texture_array(len(loaded_textures))
        self.texture_array.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.texture_array.set_magfilter(SamplerState.FT_nearest)
        self.texture_array.set_anisotropic_degree(16)

        for i, texture_name in enumerate(loaded_textures):
            try:
                texture = PNMImage()
                texture.read(f"./assets/textures/voxels/{texture_name}.png")
                self.texture_array.load(texture, z=i, n=0)
            except Exception:
                print_warning(f"failed to load texture '{texture_name}' (wrong format)")

    def validate_type(self, type: dict) -> str:
        keys = {"index": int, "textures": list, "occlusion": bool, "collision": bool}
        texture_names = type["textures"]

        for key, value in keys.items():
            if key not in type.keys():
                return f"missing key '{key}'"

            if not isinstance(type[key], value):
                return f"key '{key}' has wrong type"

        if len(texture_names) not in (1, 3):
            return "wrong texture definition"

        for texture_name in texture_names:
            if not os.path.isfile(f"./assets/textures/voxels/{texture_name}.png"):
                return f"missing texture '{texture_name}'"


resource_loader = ResourceLoader()
