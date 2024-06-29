from ursina import Entity, Vec3, held_keys, time, color, camera, mouse, clamp, lerp

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

        self.apply_settings()


    def apply_settings(self):
        self.mouse_sensitivity = settings.settings["mouse_sensitivity"]
        self.fov = settings.settings["fov"]
        camera.fov = self.fov


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
        from src.chunk_handler import instance as chunk_handler

        if not chunk_handler.finished_loading:
            return

        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

        if self.rotation_y > 360:
            self.rotation_y -= 360

        elif self.rotation_y < -360:
            self.rotation_y += 360

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        if self.noclip_mode:
            self.direction = Vec3(self.camera_pivot.forward * (held_keys["w"] - held_keys["s"])
                              + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            self.direction += self.up * (held_keys["e"] - held_keys["q"])

            self.velocity = lerp(self.velocity, self.direction * self.noclip_speed, self.noclip_acceleration * time.dt)

        else:
            if self.grounded and held_keys["space"]:
                self.velocity.y = 2 * (self.fall_speed * self.gravity * self.jump_height)**.5

            self.direction = Vec3(self.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            if held_keys["left shift"]:
                self.direction *= self.sprint_multiplier
                camera.fov = lerp(camera.fov, self.fov * self.fov_multiplier, self.acceleration * time.dt)

            else:
                camera.fov = lerp(camera.fov, self.fov, self.acceleration * time.dt)

            self.velocity.xz = lerp(self.velocity, self.direction * self.walk_speed, self.acceleration * time.dt).xz
            self.velocity.y = lerp(self.velocity.y, -self.fall_speed, self.gravity * time.dt)

            self.grounded = False

            for _ in range(3):
                velocity = self.velocity * time.dt
                collisions = []

                for i in range(3 * 3 * 4):
                    offset = Vec3(i // 3 // 4 - 1,
                                  i // 3 % 4 - 2,
                                  i % 3 % 4 - 1)

                    position = round(self.position + velocity + offset, ndigits=0)

                    entity_id = chunk_handler.get_entity_id(position)

                    if not entity_id:
                        continue

                    collision = resource_loader.entity_data[entity_id].collision

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


    def input(self, key):
        if key == "n":
            self.noclip_mode = not self.noclip_mode


    def on_enable(self):
        self.cursor.enable()
        mouse.locked = True


    def on_disable(self):
        self.cursor.disable()
        mouse.locked = False

instance = Player(enabled=False)
