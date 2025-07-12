import os
import json
import numpy as np

from queue import Queue
from ursina import Entity, Vec3, print_info, print_warning

from src.voxel_chunk import VoxelChunk
from src.settings import instance as settings
from src.resource_loader import instance as resource_loader
from c_extensions import WorldGenerator


class ChunkManager(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.updating = False
        self.world_loaded = False
        self.finished_loading = False # Used to disable loading screen
        self.set_player_position = False # If set to true, the player position is set to (0, terrain height, 0) after loading finished.
        self.player_chunk = (0, 0, 0) # Used to determine if the player crossed a chunk border
        self.chunks_to_load = Queue()
        self.chunks_to_unload = Queue()
        self.chunks_to_update = Queue()
        self.chunk_objects = {}
        self.loaded_chunks = {}

        self.world_generator = WorldGenerator(np.asarray(resource_loader.voxel_types))

        self.chunk_size = 32

        self.reload()


    def reload(self):
        # Loads settings stored in settings.json

        from src.player import instance as player

        self.render_distance = settings.settings["render_distance"]
        self.world_size = self.render_distance * 2 + 1

        self.chunk_updates = settings.settings["chunk_updates"]

        if self.world_loaded:
            self.player_chunk = self.get_chunk_id(player.position)
            self.update_chunks_all()


    def create_world(self, world_name, seed):
        if os.path.exists(f"./saves/{world_name}/"):
            return

        os.makedirs(f"./saves/{world_name}/chunks/", exist_ok=True)
        world_data = {"seed": seed, "player_position": [0.0, 0.0, 0.0], "player_rotation": [0.0, 0.0], "player_noclip": False}

        self.set_player_position = True

        with open(f"./saves/{world_name}/data.json", "w+") as file:
            json.dump(world_data, file, indent=4)

        return self.load_world(world_name)


    def delete_world(self, world_name):
        if os.path.isfile(f"./saves/{world_name}/data.json"):
            os.remove(f"./saves/{world_name}/data.json")

        if os.path.exists(f"./saves/{world_name}/chunks"):
            files = os.listdir(f"./saves/{world_name}/chunks/")

            for file in files:
                os.remove(f"./saves/{world_name}/chunks/{file}")

            os.removedirs(f"./saves/{world_name}/chunks")

        if os.path.exists(f"./saves/{world_name}"):
            os.removedirs(f"./saves/{world_name}")


    def load_world(self, world_name):
        from src.player import instance as player

        if self.world_loaded:
            return

        self.world_name = world_name

        if not os.path.exists(f"./saves/{world_name}/chunks"):
            return

        if not os.path.isfile(f"./saves/{world_name}/data.json"):
            return

        with open(f"./saves/{world_name}/data.json") as file:
            self.world_data = json.load(file)

        # Validate file content
        keys = {"seed": int, "player_position": list, "player_rotation": list, "player_noclip": bool}
        player_position = self.world_data["player_position"]
        player_rotation = self.world_data["player_rotation"]

        for key, value in keys.items():
            if not key in self.world_data.keys():
                print_warning(f"Failed to load world \'{world_name}\' (missing key \'{key}\' in data.json)")
                return

            if not isinstance(self.world_data[key], value):
                print_warning(f"Failed to load world \'{world_name}\' (key \'{key}\' has wrong type in data.json)")
                return

        if not len(player_position) == 3:
            print_warning(f"Failed to load world \'{world_name}\' (wrong player position in data.json)")
            return

        for item in player_position:
            if not type(item) == float:
                print_warning(f"Failed to load world \'{world_name}\' (wrong player position in data.json)")
                return

        if not len(player_rotation) == 2:
            print_warning(f"Failed to load world \'{world_name}\' (wrong player rotation in data.json)")
            return

        for item in player_rotation:
            if not type(item) == float:
                print_warning(f"Failed to load world \'{world_name}\' (wrong player rotation in data.json)")
                return

        player.position = self.world_data["player_position"]
        player.rotation_y = self.world_data["player_rotation"][0]
        player.camera_pivot.rotation_x = self.world_data["player_rotation"][1]
        player.noclip_mode = self.world_data["player_noclip"]

        self.seed = self.world_data["seed"]

        self.finished_loading = False
        self.world_loaded = True

        self.player_chunk = self.get_chunk_id(player.position)
        self.update_chunks_all()

        print_info(f"loaded world {self.world_name} with seed {self.seed}")

        return True


    def unload_world(self):
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


    def get_chunk_id(self, position):
        return (int(((position[0] + 0.5) // self.chunk_size) * self.chunk_size),
                int(((position[1] + 0.5) // self.chunk_size) * self.chunk_size),
                int(((position[2] + 0.5) // self.chunk_size) * self.chunk_size))


    def get_voxel_id(self, position):
        if not self.world_loaded:
            return

        chunk_id = self.get_chunk_id(position)

        if not chunk_id in self.loaded_chunks:
            return

        x_position = round(position[0] - chunk_id[0])
        y_position = round(position[1] - chunk_id[1])
        z_position = round(position[2] - chunk_id[2])

        index = x_position * self.chunk_size * self.chunk_size + y_position * self.chunk_size + z_position

        return self.loaded_chunks[chunk_id][index]


    def modify_voxel(self, position, voxel_id):
        if not self.world_loaded:
            return

        chunk_id = self.get_chunk_id(position)

        if not chunk_id in self.loaded_chunks:
            return

        x_position = round(position[0] - chunk_id[0])
        y_position = round(position[1] - chunk_id[1])
        z_position = round(position[2] - chunk_id[2])

        index = x_position * self.chunk_size * self.chunk_size + y_position * self.chunk_size + z_position

        self.loaded_chunks[chunk_id][index] = voxel_id

        self.update_chunk(chunk_id)

        # Check if neighboring chunks need to be updated
        if x_position == 0:
            self.update_chunk((chunk_id[0] - self.chunk_size, chunk_id[1], chunk_id[2]))

        if x_position == self.chunk_size - 1:
            self.update_chunk((chunk_id[0] + self.chunk_size, chunk_id[1], chunk_id[2]))

        if y_position == 0:
            self.update_chunk((chunk_id[0], chunk_id[1] - self.chunk_size, chunk_id[2]))

        if y_position == self.chunk_size - 1:
            self.update_chunk((chunk_id[0], chunk_id[1] + self.chunk_size, chunk_id[2]))

        if z_position == 0:
            self.update_chunk((chunk_id[0], chunk_id[1], chunk_id[2] - self.chunk_size))

        if z_position == self.chunk_size - 1:
            self.update_chunk((chunk_id[0], chunk_id[1], chunk_id[2] + self.chunk_size))


    def get_terrain_height(self, position: Vec3):
        current_position = round(position, ndigits=0)

        voxel_id = self.get_voxel_id(current_position)

        if voxel_id and resource_loader.voxel_types[voxel_id - 1].collision:
            step_y = 1
        else:
            step_y = -1

        for _ in range(50):
            voxel_id = self.get_voxel_id(current_position)

            if voxel_id and resource_loader.voxel_types[voxel_id - 1].collision:
                if step_y < 0:
                    return current_position

            elif step_y > 0:
                return current_position - Vec3.up

            current_position.y += step_y


    def load_chunk(self, chunk_id: tuple):
        if chunk_id in self.loaded_chunks:
            return

        filename = f"./saves/{self.world_name}/chunks/{chunk_id}.npy"

        if os.path.exists(filename):
            voxels = np.load(filename)

        else:
            voxels = self.world_generator.generate_voxels(self.chunk_size, self.seed, np.array(chunk_id, dtype=np.intc))

        self.loaded_chunks[chunk_id] = voxels

        for id in [(-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            neighbor_id = (id[0] * self.chunk_size + chunk_id[0],
                           id[1] * self.chunk_size + chunk_id[1],
                           id[2] * self.chunk_size + chunk_id[2])

            if neighbor_id in self.loaded_chunks:
                self.chunks_to_update.put(neighbor_id)

        self.chunks_to_update.put(chunk_id)


    def unload_chunk(self, chunk_id: tuple):
        if not chunk_id in self.loaded_chunks:
            return

        if chunk_id in self.chunk_objects:
            chunk = self.chunk_objects.pop(chunk_id)
            chunk.remove_node()

        filename = f"./saves/{self.world_name}/chunks/{chunk_id}.npy"

        voxels = self.loaded_chunks[chunk_id]

        np.save(filename, voxels)

        self.loaded_chunks.pop(chunk_id)


    def update_chunk(self, chunk_id: tuple):
        if not chunk_id in self.loaded_chunks:
            return

        neighbors = np.zeros(6, dtype=np.longlong)

        for i, id in enumerate([(-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, 1, 0), (0, 0, 1)]):
            neighbor_id = (id[0] * self.chunk_size + chunk_id[0],
                           id[1] * self.chunk_size + chunk_id[1],
                           id[2] * self.chunk_size + chunk_id[2])

            if neighbor_id in self.loaded_chunks:
                neighbors[i] = self.loaded_chunks[neighbor_id].ctypes.data

        vertex_data = self.world_generator.generate_mesh(self.chunk_size, self.loaded_chunks[chunk_id], neighbors)

        if len(vertex_data) == 0:
            if chunk_id in self.chunk_objects:
                chunk = self.chunk_objects.pop(chunk_id)
                chunk.remove_node()

            return

        if not chunk_id in self.chunk_objects:
            chunk = VoxelChunk(self.chunk_size, shader=resource_loader.voxel_shader)
            chunk.set_shader_input("texture_array", resource_loader.texture_array)
            chunk.set_pos(chunk_id)
            chunk.reparent_to(self)
            self.chunk_objects[chunk_id] = chunk

        chunk = self.chunk_objects[chunk_id]

        chunk.update(vertex_data)


    def update_chunks_all(self):
        chunk_ids = []

        for i in range(self.world_size**3):
            x = i // self.world_size // self.world_size - self.render_distance
            y = i // self.world_size % self.world_size - self.render_distance
            z = i % self.world_size - self.render_distance

            chunk_id = (int(x * self.chunk_size + self.player_chunk[0]),
                        int(y * self.chunk_size + self.player_chunk[1]),
                        int(z * self.chunk_size + self.player_chunk[2]))

            chunk_ids.append(chunk_id)

        for chunk_id in chunk_ids:
            if not chunk_id in self.loaded_chunks:
                self.chunks_to_load.put(chunk_id)

        for chunk_id in self.loaded_chunks.copy():
            if not chunk_id in chunk_ids:
                self.chunks_to_unload.put(chunk_id)


    def update_chunks_slice_x(self, direction: int):
        x = self.render_distance * direction
        for i in range(self.world_size**2):
            y = i // self.world_size - self.render_distance
            z = i % self.world_size - self.render_distance

            self.chunks_to_load.put((int((x + direction) * self.chunk_size + self.player_chunk[0]),
                                     int(y * self.chunk_size + self.player_chunk[1]),
                                     int(z * self.chunk_size + self.player_chunk[2])))

            self.chunks_to_unload.put((int(-x * self.chunk_size + self.player_chunk[0]),
                                       int(y * self.chunk_size + self.player_chunk[1]),
                                       int(z * self.chunk_size + self.player_chunk[2])))


    def update_chunks_slice_y(self, direction: int):
        y = self.render_distance * direction
        for i in range(self.world_size**2):
            x = i // self.world_size - self.render_distance
            z = i % self.world_size - self.render_distance

            self.chunks_to_load.put((int(x * self.chunk_size + self.player_chunk[0]),
                                     int((y + direction) * self.chunk_size + self.player_chunk[1]),
                                     int(z * self.chunk_size + self.player_chunk[2])))

            self.chunks_to_unload.put((int(x * self.chunk_size + self.player_chunk[0]),
                                       int(-y * self.chunk_size + self.player_chunk[1]),
                                       int(z * self.chunk_size + self.player_chunk[2])))


    def update_chunks_slice_z(self, direction: int):
        z = self.render_distance * direction
        for i in range(self.world_size**2):
            y = i // self.world_size - self.render_distance
            x = i % self.world_size - self.render_distance

            self.chunks_to_load.put((int(x * self.chunk_size + self.player_chunk[0]),
                                     int(y * self.chunk_size + self.player_chunk[1]),
                                     int((z + direction) * self.chunk_size + self.player_chunk[2])))

            self.chunks_to_unload.put((int(x * self.chunk_size + self.player_chunk[0]),
                                       int(y * self.chunk_size + self.player_chunk[1]),
                                       int(-z * self.chunk_size + self.player_chunk[2])))


    def update(self):
        from src.player import instance as player

        if not self.world_loaded:
            return

        self.updating = True

        new_player_chunk = self.get_chunk_id(player.position)

        if not self.player_chunk == new_player_chunk:
            x_diff = (new_player_chunk[0] - self.player_chunk[0]) / self.chunk_size
            y_diff = (new_player_chunk[1] - self.player_chunk[1]) / self.chunk_size
            z_diff = (new_player_chunk[2] - self.player_chunk[2]) / self.chunk_size

            if x_diff > 1 or y_diff > 1 or z_diff > 1:
                self.player_chunk = new_player_chunk
                self.update_chunks_all()
                return

            if abs(x_diff) == 1:
                self.update_chunks_slice_x(x_diff)

            if abs(y_diff) == 1:
                self.update_chunks_slice_y(y_diff)

            if abs(z_diff) == 1:
                self.update_chunks_slice_z(z_diff)

            self.player_chunk = new_player_chunk

        if not self.chunks_to_load.empty():
            for _ in range(min(self.chunk_updates, self.chunks_to_load.qsize())):
                chunk_id = self.chunks_to_load.get()
                self.load_chunk(chunk_id)

        elif not self.chunks_to_unload.empty():
            for _ in range(min(self.chunk_updates, self.chunks_to_unload.qsize())):
                chunk_id = self.chunks_to_unload.get()
                self.unload_chunk(chunk_id)

        elif not self.chunks_to_update.empty():
            for _ in range(min(self.chunk_updates, self.chunks_to_update.qsize())):
                chunk_id = self.chunks_to_update.get()
                self.update_chunk(chunk_id)

        else:
            self.updating = False
            self.finished_loading = True

            if self.set_player_position:
                player_position = self.get_terrain_height(Vec3(0))

                if player_position:
                    player.position = player_position + Vec3(0, 2, 0)

                self.set_player_position = False


instance = ChunkManager()