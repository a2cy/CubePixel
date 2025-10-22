import os
import json
import numpy as np

from queue import Queue
from ursina import Entity, Vec3, print_info, print_warning

from .voxel_chunk import VoxelChunk
from .settings import instance as settings
from .resource_loader import instance as resource_loader
from c_extensions import WorldGenerator


CHUNK_SIZE = 32


class ChunkManager(Entity):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.updating = False
        self.world_loaded = False
        self.world_name = None
        self.finished_loading = False  # Used to disable loading screen
        self.player_to_terrain = False  # If set to true, the player position is set to (0, terrain height, 0) after loading finished.
        self.player_chunk = (0, 0, 0)  # Used to determine if the player crossed a chunk border
        self.chunks_to_load = Queue()
        self.chunks_to_unload = Queue()
        self.chunks_to_update = Queue()
        self.chunk_objects = {}
        self.loaded_chunks = {}

        self.world_generator = WorldGenerator(resource_loader.texture_types, resource_loader.occlusion_types)

        self.reload()

    def reload(self) -> None:
        # Loads settings stored in settings.json

        from src.player import instance as player

        self.render_distance = settings.settings["render_distance"]
        self.world_size = self.render_distance * 2 + 1

        self.chunk_updates = settings.settings["chunk_updates"]

        if not self.world_loaded:
            return

        for chunk in self.chunk_objects.values():
            chunk.set_shader_input("u_fog_distance", self.render_distance * CHUNK_SIZE * 2)

        self.player_chunk = self.get_chunk_id(player.position)
        self.update_chunks_all()

    def validate_world(self, world_name: str) -> bool:
        keys = {"seed": int, "player_position": list, "player_rotation": list, "player_noclip": bool}
        player_position = self.world_data["player_position"]
        player_rotation = self.world_data["player_rotation"]

        for key, value in keys.items():
            if key not in self.world_data.keys():
                print_warning(f"Failed to load world '{world_name}' (missing key '{key}' in data.json)")
                return

            if not isinstance(self.world_data[key], value):
                print_warning(f"Failed to load world '{world_name}' (key '{key}' has wrong type in data.json)")
                return

        if not len(player_position) == 3:
            print_warning(f"Failed to load world '{world_name}' (invalid player position in data.json)")
            return

        for item in player_position:
            if not (isinstance(item, (int, float))):
                print_warning(f"Failed to load world '{world_name}' (invalid player position in data.json)")
                return

        if not len(player_rotation) == 2:
            print_warning(f"Failed to load world '{world_name}' (invalid player rotation in data.json)")
            return

        for item in player_rotation:
            if not (isinstance(item, (int, float))):
                print_warning(f"Failed to load world '{world_name}' (invalid player rotation in data.json)")
                return

        return True

    def create_world(self, world_name: str, seed: int) -> bool:
        if os.path.exists(f"./saves/{world_name}/"):
            return

        os.makedirs(f"./saves/{world_name}/chunks/", exist_ok=True)
        world_data = {"seed": seed, "player_position": [0.0, 0.0, 0.0], "player_rotation": [0.0, 0.0], "player_noclip": False}

        self.player_to_terrain = True

        with open(f"./saves/{world_name}/data.json", "w+") as file:
            json.dump(world_data, file, indent=4)

        return self.load_world(world_name)

    def delete_world(self, world_name: str) -> None:
        if os.path.isfile(f"./saves/{world_name}/data.json"):
            os.remove(f"./saves/{world_name}/data.json")

        if os.path.exists(f"./saves/{world_name}/chunks"):
            files = os.listdir(f"./saves/{world_name}/chunks/")

            for file in files:
                os.remove(f"./saves/{world_name}/chunks/{file}")

            os.removedirs(f"./saves/{world_name}/chunks")

        if os.path.exists(f"./saves/{world_name}"):
            os.removedirs(f"./saves/{world_name}")

    def load_world(self, world_name: str) -> bool:
        from src.player import instance as player

        if self.world_loaded:
            return

        if not os.path.exists(f"./saves/{world_name}/chunks"):
            print_warning(f"Failed to load world '{world_name}' (missing folder)")
            return

        if not os.path.isfile(f"./saves/{world_name}/data.json"):
            print_warning(f"Failed to load world '{world_name}' (missing data.json)")
            return

        try:
            with open(f"./saves/{world_name}/data.json") as file:
                self.world_data = json.load(file)
        except Exception as exeption:
            print_warning(f"Failed to load world '{world_name}' (invalid data.json) \n {exeption}")
            return

        if not self.validate_world(world_name):
            return

        player.position = self.world_data["player_position"]
        player.rotation_y = self.world_data["player_rotation"][0]
        player.camera_pivot.rotation_x = self.world_data["player_rotation"][1]
        player.noclip_mode = self.world_data["player_noclip"]

        self.seed = self.world_data["seed"]

        self.finished_loading = False
        self.world_loaded = True
        self.world_name = world_name

        self.player_chunk = self.get_chunk_id(player.position)
        self.update_chunks_all()

        print_info(f"loaded world {self.world_name} with seed {self.seed}")

        return True

    def unload_world(self) -> None:
        from src.player import instance as player

        if not self.world_loaded:
            return

        self.world_loaded = False
        self.chunks_to_load = Queue()
        self.chunks_to_unload = Queue()
        self.chunks_to_update = Queue()

        for chunk_id in self.loaded_chunks.copy():
            self.unload_chunk(chunk_id)

        with open(f"./saves/{self.world_name}/data.json", "w+") as file:
            self.world_data["player_position"] = list(player.position)
            self.world_data["player_rotation"] = [player.rotation_y, player.camera_pivot.rotation_x]
            self.world_data["player_noclip"] = player.noclip_mode

            json.dump(self.world_data, file, indent=4)

        print_info(f"unloaded world {self.world_name}")

    def get_chunk_id(self, position: Vec3) -> tuple:
        return (
            int(((position[0] + 0.5) // CHUNK_SIZE) * CHUNK_SIZE),
            int(((position[1] + 0.5) // CHUNK_SIZE) * CHUNK_SIZE),
            int(((position[2] + 0.5) // CHUNK_SIZE) * CHUNK_SIZE),
        )

    def get_voxel_id(self, position: Vec3) -> int:
        if not self.world_loaded:
            return

        chunk_id = self.get_chunk_id(position)

        if chunk_id not in self.loaded_chunks:
            return

        x_position = round(position[0] - chunk_id[0])
        y_position = round(position[1] - chunk_id[1])
        z_position = round(position[2] - chunk_id[2])

        index = x_position * CHUNK_SIZE * CHUNK_SIZE + y_position * CHUNK_SIZE + z_position

        return self.loaded_chunks[chunk_id][index]

    def modify_voxel(self, position: Vec3, voxel_id: int) -> None:
        if not self.world_loaded:
            return

        chunk_id = self.get_chunk_id(position)

        if chunk_id not in self.loaded_chunks:
            return

        x_position = round(position[0] - chunk_id[0])
        y_position = round(position[1] - chunk_id[1])
        z_position = round(position[2] - chunk_id[2])

        index = x_position * CHUNK_SIZE * CHUNK_SIZE + y_position * CHUNK_SIZE + z_position

        self.loaded_chunks[chunk_id][index] = voxel_id

        self.update_mesh(chunk_id)

        # Check if neighboring chunks need to be updated
        if x_position == 0:
            self.update_mesh((chunk_id[0] - CHUNK_SIZE, chunk_id[1], chunk_id[2]))

        if x_position == CHUNK_SIZE - 1:
            self.update_mesh((chunk_id[0] + CHUNK_SIZE, chunk_id[1], chunk_id[2]))

        if y_position == 0:
            self.update_mesh((chunk_id[0], chunk_id[1] - CHUNK_SIZE, chunk_id[2]))

        if y_position == CHUNK_SIZE - 1:
            self.update_mesh((chunk_id[0], chunk_id[1] + CHUNK_SIZE, chunk_id[2]))

        if z_position == 0:
            self.update_mesh((chunk_id[0], chunk_id[1], chunk_id[2] - CHUNK_SIZE))

        if z_position == CHUNK_SIZE - 1:
            self.update_mesh((chunk_id[0], chunk_id[1], chunk_id[2] + CHUNK_SIZE))

    def get_terrain_height(self, position: Vec3) -> Vec3:
        current_position = round(position, ndigits=0)

        voxel_id = self.get_voxel_id(current_position)

        if voxel_id and resource_loader.collision_types[voxel_id - 1]:
            step_y = 1
        else:
            step_y = -1

        for _ in range(50):
            voxel_id = self.get_voxel_id(current_position)

            if voxel_id and resource_loader.collision_types[voxel_id - 1]:
                if step_y < 0:
                    return current_position

            elif step_y > 0:
                return current_position - Vec3.up

            current_position.y += step_y

    def load_chunk(self, chunk_id: tuple) -> None:
        if chunk_id in self.loaded_chunks:
            return

        filename = f"./saves/{self.world_name}/chunks/{chunk_id}.npy"

        if os.path.exists(filename):
            voxels = np.load(filename)

        else:
            voxels = self.world_generator.generate_voxels(CHUNK_SIZE, self.seed, *chunk_id)

        self.loaded_chunks[chunk_id] = voxels

        for id in [(-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            neighbor_id = (
                id[0] * CHUNK_SIZE + chunk_id[0],
                id[1] * CHUNK_SIZE + chunk_id[1],
                id[2] * CHUNK_SIZE + chunk_id[2],
            )

            if neighbor_id in self.chunk_objects:
                self.chunks_to_update.put(neighbor_id)

        self.chunks_to_update.put(chunk_id)

    def unload_chunk(self, chunk_id: tuple) -> None:
        if chunk_id not in self.loaded_chunks:
            return

        if chunk_id in self.chunk_objects:
            chunk = self.chunk_objects.pop(chunk_id)
            chunk.remove_node()

        filename = f"./saves/{self.world_name}/chunks/{chunk_id}.npy"

        np.save(filename, self.loaded_chunks.pop(chunk_id))

    def update_mesh(self, chunk_id: tuple) -> None:
        if chunk_id not in self.loaded_chunks:
            return

        neighbors = np.zeros(6, dtype=np.longlong)

        for i, id in enumerate([(-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, 1, 0), (0, 0, 1)]):
            neighbor_id = (
                id[0] * CHUNK_SIZE + chunk_id[0],
                id[1] * CHUNK_SIZE + chunk_id[1],
                id[2] * CHUNK_SIZE + chunk_id[2],
            )

            if neighbor_id in self.loaded_chunks:
                neighbors[i] = self.loaded_chunks[neighbor_id].ctypes.data

        vertex_data = self.world_generator.generate_mesh(CHUNK_SIZE, self.loaded_chunks[chunk_id], neighbors)

        if len(vertex_data) == 0:
            if chunk_id in self.chunk_objects:
                chunk = self.chunk_objects.pop(chunk_id)
                chunk.remove_node()

            return

        if chunk_id not in self.chunk_objects:
            chunk = VoxelChunk(CHUNK_SIZE, shader=resource_loader.voxel_shader)
            chunk.set_shader_input("u_fog_distance", self.render_distance * CHUNK_SIZE * 2)
            chunk.set_shader_input("u_texture_array", resource_loader.texture_array)
            chunk.set_pos(chunk_id)
            chunk.reparent_to(self)
            self.chunk_objects[chunk_id] = chunk

        chunk = self.chunk_objects[chunk_id]

        chunk.update(vertex_data)

    def update_chunks_all(self) -> None:
        chunk_ids = set()

        for i in range(self.world_size**3):
            x = i // (self.world_size * self.world_size) - self.render_distance
            y = i // self.world_size % self.world_size - self.render_distance
            z = i % self.world_size - self.render_distance

            chunk_ids.add(
                (
                    int(x * CHUNK_SIZE + self.player_chunk[0]),
                    int(y * CHUNK_SIZE + self.player_chunk[1]),
                    int(z * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

        for chunk_id in chunk_ids:
            if chunk_id not in self.loaded_chunks:
                self.chunks_to_load.put(chunk_id)

        for chunk_id in self.loaded_chunks.copy():
            if chunk_id not in chunk_ids:
                self.chunks_to_unload.put(chunk_id)

    def update_chunks_slice_x(self, direction: int) -> None:
        x = self.render_distance * direction

        for i in range(self.world_size**2):
            y = i // self.world_size - self.render_distance
            z = i % self.world_size - self.render_distance

            self.chunks_to_load.put(
                (
                    int((x + direction) * CHUNK_SIZE + self.player_chunk[0]),
                    int(y * CHUNK_SIZE + self.player_chunk[1]),
                    int(z * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

            self.chunks_to_unload.put(
                (
                    int(-x * CHUNK_SIZE + self.player_chunk[0]),
                    int(y * CHUNK_SIZE + self.player_chunk[1]),
                    int(z * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

    def update_chunks_slice_y(self, direction: int) -> None:
        y = self.render_distance * direction

        for i in range(self.world_size**2):
            x = i // self.world_size - self.render_distance
            z = i % self.world_size - self.render_distance

            self.chunks_to_load.put(
                (
                    int(x * CHUNK_SIZE + self.player_chunk[0]),
                    int((y + direction) * CHUNK_SIZE + self.player_chunk[1]),
                    int(z * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

            self.chunks_to_unload.put(
                (
                    int(x * CHUNK_SIZE + self.player_chunk[0]),
                    int(-y * CHUNK_SIZE + self.player_chunk[1]),
                    int(z * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

    def update_chunks_slice_z(self, direction: int) -> None:
        z = self.render_distance * direction

        for i in range(self.world_size**2):
            y = i // self.world_size - self.render_distance
            x = i % self.world_size - self.render_distance

            self.chunks_to_load.put(
                (
                    int(x * CHUNK_SIZE + self.player_chunk[0]),
                    int(y * CHUNK_SIZE + self.player_chunk[1]),
                    int((z + direction) * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

            self.chunks_to_unload.put(
                (
                    int(x * CHUNK_SIZE + self.player_chunk[0]),
                    int(y * CHUNK_SIZE + self.player_chunk[1]),
                    int(-z * CHUNK_SIZE + self.player_chunk[2]),
                )
            )

    def update(self) -> None:
        from src.player import instance as player

        if not self.world_loaded:
            return

        self.updating = True

        new_player_chunk = self.get_chunk_id(player.position)

        if not self.player_chunk == new_player_chunk:
            x_diff = (new_player_chunk[0] - self.player_chunk[0]) / CHUNK_SIZE
            y_diff = (new_player_chunk[1] - self.player_chunk[1]) / CHUNK_SIZE
            z_diff = (new_player_chunk[2] - self.player_chunk[2]) / CHUNK_SIZE

            if x_diff > 1 or y_diff > 1 or z_diff > 1:
                self.player_chunk = new_player_chunk
                self.update_chunks_all()

            else:
                if x_diff:
                    self.update_chunks_slice_x(x_diff)

                if y_diff:
                    self.update_chunks_slice_y(y_diff)

                if z_diff:
                    self.update_chunks_slice_z(z_diff)

                self.player_chunk = new_player_chunk

        if not self.chunks_to_load.empty():
            for _ in range(min(self.chunk_updates, self.chunks_to_load.unfinished_tasks)):
                chunk_id = self.chunks_to_load.get()
                self.load_chunk(chunk_id)
                self.chunks_to_load.task_done()

        elif not self.chunks_to_unload.empty():
            for _ in range(min(self.chunk_updates, self.chunks_to_unload.unfinished_tasks)):
                chunk_id = self.chunks_to_unload.get()
                self.unload_chunk(chunk_id)
                self.chunks_to_unload.task_done()

        elif not self.chunks_to_update.empty():
            for _ in range(min(self.chunk_updates, self.chunks_to_update.unfinished_tasks)):
                chunk_id = self.chunks_to_update.get()
                self.update_mesh(chunk_id)
                self.chunks_to_update.task_done()

        else:
            self.updating = False
            self.finished_loading = True

            if self.player_to_terrain:
                terrain_height = self.get_terrain_height(Vec3(0))

                if terrain_height:
                    player.position = terrain_height + Vec3(0, 2, 0)

                self.player_to_terrain = False


instance = ChunkManager()
