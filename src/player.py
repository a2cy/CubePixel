from ursina import Entity, Vec3, held_keys, time, color, clamp, lerp, camera, mouse

from src.settings import instance as settings
from src.resource_loader import instance as resource_loader


class AABB:

    def __init__(self, position, origin, scale):
        self.position = position
        self.origin = origin
        self.scale = scale


    @property
    def x(self):
        return self.position.x + self.origin.x

    @property
    def y(self):
        return self.position.y + self.origin.y

    @property
    def z(self):
        return self.position.z + self.origin.z

    @property
    def x_1(self):
        return self.position.x + self.origin.x - self.scale.x / 2

    @property
    def y_1(self):
        return self.position.y + self.origin.y - self.scale.y / 2

    @property
    def z_1(self):
        return self.position.z + self.origin.z - self.scale.z / 2

    @property
    def x_2(self):
        return self.position.x + self.origin.x + self.scale.x / 2

    @property
    def y_2(self):
        return self.position.y + self.origin.y + self.scale.y / 2

    @property
    def z_2(self):
        return self.position.z + self.origin.z + self.scale.z / 2


class Player(Entity):

    def __init__(self, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        self.selector = Entity(model="cube", shader=resource_loader.selector_shader, scale=1.005)

        super().__init__(**kwargs)

        self.walk_speed = 6
        self.fall_speed = 32
        self.gravity = 1.8
        self.acceleration = 16
        self.jump_height = 1.2
        self.sprint_multiplier = 1.6

        self.noclip_speed = 24
        self.noclip_acceleration = 6
        self.noclip_mode = False

        self.player_collider = AABB(Vec3(0), Vec3(0, -.8, 0), Vec3(.8, 1.8, .8))
        self.entity_collider = AABB(Vec3(0), Vec3(0), Vec3(1))

        self.fov_multiplier = 1.12
        self.camera_pivot = Entity(parent=self)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0,0,0)
        camera.rotation = Vec3(0,0,0)

        self.grounded = False
        self.direction = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)

        self.reload()


    def reload(self):
        self.mouse_sensitivity = settings.settings["mouse_sensitivity"]
        self.fov = settings.settings["fov"]
        camera.fov = self.fov


    def update_selector(self, position, direction, max_distance):
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

            entity_id = chunk_manager.get_voxel_id(current_position)

            if entity_id == None:
                continue

            if not entity_id == resource_loader.voxel_index["air"]:
                self.selector.position = current_position
                self.selector.hit_normal = hit_normal
                self.selector.enabled = True
                return

        self.selector.enabled = False


    def aabb_broadphase(self, collider_1, collider_2, direction):
        x_1 = min(collider_1.x_1, collider_1.x_1 + direction.x)
        y_1 = min(collider_1.y_1, collider_1.y_1 + direction.y)
        z_1 = min(collider_1.z_1, collider_1.z_1 + direction.z)

        x_2 = max(collider_1.x_2, collider_1.x_2 + direction.x)
        y_2 = max(collider_1.y_2, collider_1.y_2 + direction.y)
        z_2 = max(collider_1.z_2, collider_1.z_2 + direction.z)

        return (x_1 < collider_2.x_2 and x_2 > collider_2.x_1 and
                y_1 < collider_2.y_2 and y_2 > collider_2.y_1 and
                z_1 < collider_2.z_2 and z_2 > collider_2.z_1)


    def swept_aabb(self, collider_1, collider_2, direction):
        get_time = lambda x, y: x / y if y else float("-" * (x > 0) + "inf")

        x_entry = get_time(collider_2.x_1 - collider_1.x_2 if direction.x > 0 else collider_2.x_2 - collider_1.x_1, direction.x)
        x_exit = get_time(collider_2.x_2 - collider_1.x_1 if direction.x > 0 else collider_2.x_1 - collider_1.x_2, direction.x)

        y_entry = get_time(collider_2.y_1 - collider_1.y_2 if direction.y > 0 else collider_2.y_2 - collider_1.y_1, direction.y)
        y_exit = get_time(collider_2.y_2 - collider_1.y_1 if direction.y > 0 else collider_2.y_1 - collider_1.y_2, direction.y)

        z_entry = get_time(collider_2.z_1 - collider_1.z_2 if direction.z > 0 else collider_2.z_2 - collider_1.z_1, direction.z)
        z_exit = get_time(collider_2.z_2 - collider_1.z_1 if direction.z > 0 else collider_2.z_1 - collider_1.z_2, direction.z)

        if x_entry < 0 and y_entry < 0 and z_entry < 0:
            return 1, Vec3(0, 0, 0)

        if x_entry > 1 or y_entry > 1 or z_entry > 1:
            return 1, Vec3(0, 0, 0)

        entry_time = max(x_entry, y_entry, z_entry)
        exit_time = min(x_exit, y_exit, z_exit)

        if entry_time > exit_time:
            return 1, Vec3(0, 0, 0)

        normal_x = (0, -1 if direction.x > 0 else 1)[entry_time == x_entry]
        normal_y = (0, -1 if direction.y > 0 else 1)[entry_time == y_entry]
        normal_z = (0, -1 if direction.z > 0 else 1)[entry_time == z_entry]

        return entry_time, Vec3(normal_x, normal_y, normal_z)


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

            self.velocity = lerp(self.velocity, self.direction * self.noclip_speed, self.noclip_acceleration * min(time.dt, 0.05))

        else:
            if self.grounded and held_keys["space"]:
                self.velocity.y = 2 * (self.fall_speed * self.gravity * self.jump_height)**.5

            self.direction = Vec3(self.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            if held_keys["left shift"]:
                self.direction *= self.sprint_multiplier
                camera.fov = lerp(camera.fov, self.fov * self.fov_multiplier, self.acceleration * min(time.dt, 0.05))

            else:
                camera.fov = lerp(camera.fov, self.fov, self.acceleration * min(time.dt, 0.05))

            self.velocity.xz = lerp(self.velocity, self.direction * self.walk_speed, self.acceleration * min(time.dt, 0.05)).xz
            self.velocity.y = lerp(self.velocity.y, -self.fall_speed, self.gravity * min(time.dt, 0.05))

            self.grounded = False

            for _ in range(3):
                velocity = self.velocity * time.dt
                collisions = []

                for i in range(3 * 3 * 4):
                    offset = Vec3(i // 3 // 4 - 1,
                                  i // 3 % 4 - 2,
                                  i % 3 % 4 - 1)

                    position = round(self.position + velocity + offset, ndigits=0)

                    entity_id = chunk_manager.get_voxel_id(position)

                    if not entity_id:
                        continue

                    collision = resource_loader.voxel_types[entity_id].collision

                    if not collision:
                        continue

                    self.entity_collider.position = position

                    if self.aabb_broadphase(self.player_collider, self.entity_collider, velocity):
                        collision_time, collision_normal = self.swept_aabb(self.player_collider, self.entity_collider, velocity)

                        collisions.append((collision_time, collision_normal))

                if not collisions:
                    break

                collision_time, collision_normal = min(collisions, key= lambda x: x[0])
                collision_time -= .0001

                if collision_normal.x:
                    self.velocity.x = 0
                    self.position.x += velocity.x * collision_time

                if collision_normal.y:
                    self.velocity.y = 0
                    self.position.y += velocity.y * collision_time

                if collision_normal.z:
                    self.velocity.z = 0
                    self.position.z += velocity.z * collision_time

                if collision_normal.y == 1:
                    self.grounded = True

        self.position += self.velocity * time.dt

        self.player_collider.position = self.position

        self.update_selector(self.camera_pivot.world_position, self.camera_pivot.forward, 5)


    def input(self, key):
        from src.chunk_manager import instance as chunk_manager

        if key == "n":
            self.noclip_mode = not self.noclip_mode

        if key == "left mouse down" and self.selector.enabled:
            chunk_manager.modify_entity(self.selector.position, resource_loader.voxel_index["air"])

        if key == "right mouse down" and self.selector.enabled:
            point = self.selector.position + self.selector.hit_normal

            self.entity_collider.position = point
            if not self.aabb_broadphase(self.player_collider, self.entity_collider, Vec3(0)):
                chunk_manager.modify_entity(point, resource_loader.voxel_index["stone"])


    def on_enable(self):
        self.cursor.enable()
        mouse.locked = True


    def on_disable(self):
        self.cursor.disable()
        mouse.locked = False

instance = Player(enabled=False)
