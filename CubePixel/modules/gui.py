from ursina import *


class TitleScreen(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 scale=camera.aspect_ratio)

        self.join_button = Button(parent=self,
                                  text="Join World",
                                  position=Vec2(0, .05),
                                  scale=Vec2(.25, .075),
                                  on_click=Func(self.game.join_world))

        self.exit_button = Button(parent=self,
                                  text="Quit Game",
                                  position=Vec2(0, -.05),
                                  scale=Vec2(.25, .075),
                                  on_click=Func(application.quit))

        for key, value in kwargs.items():
            setattr(self, key, value)


class PauseScreen(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game

        self.continue_button = Button(parent=self,
                                      text="Continue Playing",
                                      position=Vec2(0, .05),
                                      scale=Vec2(.25, .075),
                                      on_click=Func(self._disable))

        self.leave_button = Button(parent=self,
                                   text="Leave World",
                                   position=Vec2(0, -.05),
                                   scale=Vec2(.25, .075),
                                   on_click=Func(self.game.leave_world))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _disable(self):
        mouse.locked = True
        self.disable()


class DebugScreen(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game

        self.position_display = Text(parent=self,
                                     position=window.top_left,
                                     origin=(-0.5, 0.5),
                                     text="")

        self.rotation_display = Text(parent=self,
                                     position=window.top_left,
                                     origin=(-0.5, 1.5),
                                     text="")

        self.update_display = Text(parent=self,
                                   position=window.top_left,
                                   origin=(-0.5, 2.5),
                                   text="")

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.position_display.text = f"{self.game.player.position}"

        self.rotation_display.text = f"{round(self.game.player.rotation[1], 5)}, {round(self.game.player.camera_pivot.rotation[0], 5)}"

        self.update_display.text = f"{self.game.chunk_handler.updating}"
