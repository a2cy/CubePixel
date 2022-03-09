from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class Player(Entity):
    def __init__(self, game):
        super().__init__(model='cube',
                         scale=Vec3(1, 1, 1))

        self.game = game
