from ursina import *


class TitleScreen(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.game = game

        self.background = Entity(parent=self,
                                 model='quad',
                                 texture='shore',
                                 scale=camera.aspect_ratio)

        self.start_button = Button(parent=self,
                                   text='Start',
                                   position=Vec2(0, .05),
                                   scale=Vec2(.25, .075),
                                   highlight_color=color.gray,
                                   on_click=Func(self.game.start_game))

        self.exit_button = Button(parent=self,
                                  text='Quit',
                                  position=Vec2(0, -.05),
                                  scale=Vec2(.25, .075),
                                  highlight_color=color.gray,
                                  on_click=Func(application.quit))
