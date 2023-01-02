import ursina


class Player(ursina.Entity):

    def __init__(self, game, **kwargs):
        super().__init__()
        self.game = game
        
        self.speed = 8
        self.acceleration = 6

        self.camera_pivot = ursina.Entity(parent=self)
        ursina.camera.parent = self.camera_pivot
        ursina.camera.position = ursina.Vec3(0,0,0)
        ursina.camera.rotation = ursina.Vec3(0,0,0)
        ursina.camera.fov = 90
        self.mouse_sensitivity = 80

        self.direction = ursina.Vec3(0,0,0)
        self.velocity = ursina.Vec3(0,0,0)

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.rotation_y += ursina.mouse.velocity[0] * self.mouse_sensitivity

        self.camera_pivot.rotation_x -= ursina.mouse.velocity[1] * self.mouse_sensitivity
        self.camera_pivot.rotation_x = ursina.clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = ursina.Vec3(
            self.camera_pivot.forward * (ursina.held_keys["w"] - ursina.held_keys["s"])
            + self.right * (ursina.held_keys["d"] - ursina.held_keys["a"])
            ).normalized()

        self.direction += self.up * (ursina.held_keys["space"] - ursina.held_keys["shift"])

        self.velocity = ursina.lerp(self.velocity, self.direction * self.speed, self.acceleration * ursina.time.dt)

        self.position += self.velocity / 100
