from ursina import Entity, Vec3, held_keys, time, camera, mouse, clamp, lerp


class AABB():

    def __init__(self, vertex_1, vertex_2):
        self.vertex_1 = vertex_1
        self.vertex_2 = vertex_2


    @property
    def x(self):
        return self.vertex_1.x

    @property
    def y(self):
        return self.vertex_1.y

    @property
    def z(self):
        return self.vertex_1.z

    @property
    def x_1(self):
        return self.vertex_2[0] + self.vertex_1.x

    @property
    def y_1(self):
        return self.vertex_2[1] + self.vertex_1.y

    @property
    def z_1(self):
        return self.vertex_2[2] + self.vertex_1.z

    @property
    def x_2(self):
        return self.vertex_2[3] + self.vertex_1.x

    @property
    def y_2(self):
        return self.vertex_2[4] + self.vertex_1.y

    @property
    def z_2(self):
        return self.vertex_2[5] + self.vertex_1.z


class Player(Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.walk_speed = 6
        self.fall_speed = 32
        self.gravity = 1.8
        self.acceleration = 16
        self.jump_height = 1.2

        self.noclip_speed = 8
        self.noclip_acceleration = 6
        self.noclip_mode = False

        self.aabb_collider = AABB(self.position, [-.4, -1.5, -.4,  .4, .4, .4])

        self.camera_pivot = Entity(parent=self)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0,0,0)
        camera.rotation = Vec3(0,0,0)
        camera.fov = 90
        self.mouse_sensitivity = self.game.settings["mouse_sensitivity"]

        self.grounded = False
        self.direction = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)

        self.aim_dot = Entity(parent=self.camera_pivot, z = 3, model="cube", scale=.02)


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
        if self.noclip_mode:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

            self.direction = Vec3(self.camera_pivot.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            self.direction += self.up * (held_keys["e"] - held_keys["q"])

            self.velocity = lerp(self.velocity, self.direction * self.noclip_speed, self.noclip_acceleration * time.dt)

            self.position += self.velocity * time.dt

        else:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

            if self.grounded and held_keys["space"]:
                self.velocity.y = 2 * (self.fall_speed * self.gravity * self.jump_height)**.5

            self.direction = Vec3(self.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()

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

                    entity_id = self.game.chunk_handler.get_entity_id(position)

                    if not entity_id:
                        continue

                    collision = self.game.entity_loader.entity_data[entity_id].collision

                    if not collision:
                        continue

                    collider = AABB(position, self.game.entity_loader.entity_data[entity_id].collider)

                    if self.aabb_broadphase(self.aabb_collider, collider, velocity):
                        collision_time, collision_normal = self.swept_aabb(self.aabb_collider, collider, velocity)

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

            self.aabb_collider.vertex_1 = self.position


    def on_enable(self):
        mouse.locked = True


    def on_disable(self):
        mouse.locked = False
