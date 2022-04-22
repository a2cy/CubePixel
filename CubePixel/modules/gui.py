from ursina import *


class TitleScreen(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs, parent=camera.ui)
        self.game = game

        self.background = Entity(parent=self,
                                 model='quad',
                                 texture='shore',
                                 scale=camera.aspect_ratio)

        self.join_button = Button(parent=self,
                                  text='Join World',
                                  position=Vec2(0, .05),
                                  scale=Vec2(.25, .075),
                                  highlight_color=color.gray,
                                  on_click=Func(self.game.join_world))

        self.exit_button = Button(parent=self,
                                  text='Quit Game',
                                  position=Vec2(0, -.05),
                                  scale=Vec2(.25, .075),
                                  highlight_color=color.gray,
                                  on_click=Func(application.quit))


class PauseScreen(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs, parent=camera.ui)
        self.game = game

        self.continue_button = Button(parent=self,
                                      text='Continue Playing',
                                      position=Vec2(0, .05),
                                      scale=Vec2(.25, .075),
                                      highlight_color=color.gray,
                                      on_click=Func(self._disable))

        self.leave_button = Button(parent=self,
                                   text='Leave World',
                                   position=Vec2(0, -.05),
                                   scale=Vec2(.25, .075),
                                   highlight_color=color.gray,
                                   on_click=Func(self.game.leave_world))

    def _disable(self):
        mouse.locked = True
        self.disable()


class DebugScreen(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs, parent=camera.ui)
        self.game = game

        self.position_display = Text(parent=self,
                                     position=window.top_left,
                                     origin=(-0.5, 0.5),
                                     text='')

        self.update_display = Text(parent=self,
                                   position=window.top_left,
                                   origin=(-0.5, 1.5),
                                   text='')

    def update(self):
        self.position_display.text = str(self.game.player.position)

        self.update_display.text = str(self.game.world.updating)
