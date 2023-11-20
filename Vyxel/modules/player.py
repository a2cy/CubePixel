from ursina import Entity, Vec3, held_keys, time, camera, mouse, clamp, lerp


class Player(Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game

        self.speed = 8
        self.acceleration = 6

        self.camera_pivot = Entity(parent=self)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0,0,0)
        camera.rotation = Vec3(0,0,0)
        camera.fov = 90
        self.mouse_sensitivity = 80

        self.direction = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.camera_pivot.forward * (held_keys["w"] - held_keys["s"])
            + self.right * (held_keys["d"] - held_keys["a"])
            ).normalized()

        self.direction += self.up * (held_keys["space"] - held_keys["shift"])

        self.velocity = lerp(self.velocity, self.direction * self.speed, self.acceleration * time.dt)

        self.position += self.velocity * time.dt


    def on_enable(self):
        mouse.locked = True


    def on_disable(self):
        mouse.locked = False
