from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class Player(FirstPersonController):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)

        self.game = game
        self.gravity = 0
        self.fov = 90
