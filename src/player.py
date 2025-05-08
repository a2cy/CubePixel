from ursina import Entity, Vec3, held_keys, time, color, clamp, lerp, camera, mouse

from src.settings import instance as settings
from src.resource_loader import instance as resource_loader


class AABBCollider:

    def __init__(self, position, origin, scale):
        self._scale = scale
        self._origin = origin
        self.position = position


    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

        self.x_1 = value.x + self._origin.x - self._scale.x / 2
        self.y_1 = value.y + self._origin.y - self._scale.y / 2
        self.z_1 = value.z + self._origin.z - self._scale.z / 2

        self.x_2 = value.x + self._origin.x + self._scale.x / 2
        self.y_2 = value.y + self._origin.y + self._scale.y / 2
        self.z_2 = value.z + self._origin.z + self._scale.z / 2


    def intersect(self, collider):
        return (self.x_1 < collider.x_2 and self.x_2 > collider.x_1 and
                self.y_1 < collider.y_2 and self.y_2 > collider.y_1 and
                self.z_1 < collider.z_2 and self.z_2 > collider.z_1)


    def collide(self, collider, direction):
        get_time = lambda x, y: x / y if y else float("-" * (x > 0) + "inf")

        no_collision = 1, None

        x_entry = get_time(collider.x_1 - self.x_2 if direction.x > 0 \
                           else collider.x_2 - self.x_1, direction.x)
        x_exit = get_time(collider.x_2 - self.x_1 if direction.x > 0 \
                          else collider.x_1 - self.x_2, direction.x)

        y_entry = get_time(collider.y_1 - self.y_2 if direction.y > 0 \
                           else collider.y_2 - self.y_1, direction.y)
        y_exit = get_time(collider.y_2 - self.y_1 if direction.y > 0 \
                          else collider.y_1 - self.y_2, direction.y)

        z_entry = get_time(collider.z_1 - self.z_2 if direction.z > 0 \
                           else collider.z_2 - self.z_1, direction.z)
        z_exit = get_time(collider.z_2 - self.z_1 if direction.z > 0 \
                          else collider.z_1 - self.z_2, direction.z)

        if x_entry < 0 and y_entry < 0 and z_entry < 0:
            return no_collision

        if x_entry > 1 or y_entry > 1 or z_entry > 1:
            return no_collision

        entry_time = max(x_entry, y_entry, z_entry)
        exit_time = min(x_exit, y_exit, z_exit)

        if entry_time > exit_time:
            return no_collision

        normal_x = (0, -1 if direction.x > 0 else 1)[entry_time == x_entry]
        normal_y = (0, -1 if direction.y > 0 else 1)[entry_time == y_entry]
        normal_z = (0, -1 if direction.z > 0 else 1)[entry_time == z_entry]

        return entry_time, Vec3(normal_x, normal_y, normal_z)


class Player(Entity):

    def __init__(self, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        self.selector = Entity(model="cube", shader=resource_loader.selector_shader, scale=1.005)

        super().__init__(**kwargs)

        self.gravity = 25
        self.walk_speed = 6
        self.max_fall_speed = 60
        self.acceleration = 16
        self.sprint_multiplier = 1.6
        self.jump_height = 1.2
        self.grounded = False

        self.noclip_speed = 24
        self.noclip_acceleration = 6
        self.noclip_mode = False

        self.player_collider = AABBCollider(Vec3(0), Vec3(0, -0.6, 0), Vec3(0.8, 1.8, 0.8))
        self.voxel_collider = AABBCollider(Vec3(0), Vec3(0), Vec3(1))

        self.fov_multiplier = 1.12
        self.camera_pivot = Entity(parent=self)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0)
        camera.rotation = Vec3(0)

        self.direction = Vec3(0)
        self.velocity = Vec3(0)

        self.reload()


    def reload(self):
        self.mouse_sensitivity = settings.settings["mouse_sensitivity"]
        self.fov = settings.settings["fov"]
        camera.fov = self.fov


    def update_selector(self, position, direction, max_distance):
        self.selector.enabled = False

        from src.chunk_manager import instance as chunk_manager

        current_position = round(position, ndigits=0)
        current_distance = 0

        direction.normalize()

        step_x = 1 if direction.x >= 0 else -1
        step_y = 1 if direction.y >= 0 else -1
        step_z = 1 if direction.z >= 0 else -1

        delta_x = 10 if direction.x == 0 else 1 / direction.x * step_x
        delta_y = 10 if direction.y == 0 else 1 / direction.y * step_y
        delta_z = 10 if direction.z == 0 else 1 / direction.z * step_z

        x_distance = delta_x * (.5 - (position.x - current_position.x) * step_x)
        y_distance = delta_y * (.5 - (position.y - current_position.y) * step_y)
        z_distance = delta_z * (.5 - (position.z - current_position.z) * step_z)

        while (current_distance < max_distance):
            if x_distance < y_distance and x_distance < z_distance:
                current_distance = x_distance
                x_distance += delta_x
                current_position.x += step_x
                hit_normal = Vec3(-step_x, 0, 0)

            elif y_distance < x_distance and y_distance < z_distance:
                current_distance = y_distance
                y_distance += delta_y
                current_position.y += step_y
                hit_normal = Vec3(0, -step_y, 0)

            else:
                current_distance = z_distance
                z_distance += delta_z
                current_position.z += step_z
                hit_normal = Vec3(0, 0, -step_z)

            voxel_id = chunk_manager.get_voxel_id(current_position)

            if voxel_id and resource_loader.voxel_types[voxel_id - 1].inventory:
                self.selector.position = current_position
                self.selector.hit_normal = hit_normal
                self.selector.enabled = True
                break


    def update(self):
        from src.chunk_manager import instance as chunk_manager

        if not chunk_manager.finished_loading:
            return

        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

        if self.rotation_y > 360:
            self.rotation_y -= 360

        elif self.rotation_y < -360:
            self.rotation_y += 360

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -89, 89)

        if self.noclip_mode:
            self.direction = Vec3(self.camera_pivot.forward * (held_keys["w"] - held_keys["s"])
                              + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            self.direction += self.up * (held_keys["e"] - held_keys["q"])

            self.velocity = lerp(self.direction * self.noclip_speed, self.velocity, .5**(self.noclip_acceleration * time.dt))

            self.position += self.velocity * time.dt

        else:
            if self.grounded and held_keys["space"]:
                self.velocity.y = (self.gravity * self.jump_height * 2)**.5

            self.direction = Vec3(self.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            if held_keys["left shift"]:
                self.direction *= self.sprint_multiplier
                camera.fov = lerp(self.fov * self.fov_multiplier, camera.fov, .5**(self.acceleration * time.dt))

            else:
                camera.fov = lerp(self.fov, camera.fov, .5**(self.acceleration * time.dt))

            self.velocity.xz = lerp(self.direction * self.walk_speed, self.velocity, .5**(self.acceleration * time.dt)).xz
            self.velocity.y = self.velocity.y - self.gravity * min(time.dt, .5)
            self.velocity.y = max(self.velocity.y, -self.max_fall_speed)

            self.grounded = False
            self.player_collider.position = self.position
            move_delta = self.velocity * time.dt

            for _ in range(4):
                collisions = []

                for i in range(3 * 3 * 4):
                    offset = Vec3(i // 3 // 4 - 1,
                                  i // 3 % 4 - 2,
                                  i % 3 % 4 - 1)

                    voxel_id = chunk_manager.get_voxel_id(self.position + move_delta + offset)

                    if not voxel_id:
                        continue

                    collision = resource_loader.voxel_types[voxel_id - 1].collision

                    if not collision:
                        continue

                    self.voxel_collider.position = round(self.position + move_delta + offset, ndigits=0)

                    collision_time, normal = self.player_collider.collide(self.voxel_collider, move_delta)

                    if normal is None:
                        continue

                    collisions.append((collision_time, normal))

                if not collisions:
                    break

                collision_time, normal = min(collisions, key=lambda x: x[0])
                collision_time *= 0.5

                if normal.x:
                    self.velocity.x = 0
                    move_delta.x = move_delta.x * collision_time

                if normal.y:
                    self.velocity.y = 0
                    move_delta.y = move_delta.y * collision_time

                if normal.z:
                    self.velocity.z = 0
                    move_delta.z = move_delta.z * collision_time

                if normal.y == 1:
                    self.grounded = True

            self.position += move_delta

        self.update_selector(self.camera_pivot.world_position, self.camera_pivot.forward, 5)


    def input(self, key):
        from src.chunk_manager import instance as chunk_manager
        from src.gui import instance as gui

        if key == "n":
            self.noclip_mode = not self.noclip_mode

        if key == "left mouse down" and self.selector.enabled:
            chunk_manager.modify_voxel(self.selector.position, 0)

        if key == "right mouse down" and self.selector.enabled:
            if not gui.inventory.selection:
                return

            point = self.selector.position + self.selector.hit_normal
            self.voxel_collider.position = point

            if not self.player_collider.intersect(self.voxel_collider):
                chunk_manager.modify_voxel(point, gui.inventory.selection[0])


    def on_enable(self):
        self.cursor.enable()
        mouse.position = Vec3(0)
        mouse.locked = True


    def on_disable(self):
        self.cursor.disable()
        mouse.locked = False


instance = Player(enabled=False)