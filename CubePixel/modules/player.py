from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class Player(FirstPersonController):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.gravity = 0
        self.fov = 90
