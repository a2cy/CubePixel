import os
import json
from ursina import *


class MainMenu(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__(parent=camera.ui)

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 scale=camera.aspect_ratio)

        self.exit_button = Button(parent=self,
                                  text="X",
                                  position=window.top_right,
                                  origin=Vec2(.8, .8),
                                  scale=Vec2(.03, .03),
                                  on_click=Func(application.quit))

        self.world_name_input_field = InputField(parent=self,
                                                 position=Vec2(0, .2))

        self.input_field_text = Text(parent=self,
                                     text="World Name",
                                     position=Vec2(0, .25),
                                     origin=Vec2(0, 0))


        def create_world_func():
            world_name = self.world_name_input_field.text.lower()
            if not world_name or os.path.exists(f"saves/{world_name}/"):
                return
            
            self.world_name_input_field.text = ""

            self.game.ui_state_handler.state = "None"
            self.game.chunk_handler.enable()
            self.game.chunk_handler.create_world(world_name, round(time.time()))
            self.game.debug_screen.enable()
            self.game.player.enable()
            mouse.locked = True

        self.new_world = Button(parent=self,
                                text="New World",
                                position=Vec2(.4, .2),
                                scale=Vec2(.25, .075),
                                on_click=Func(create_world_func))


        for key, value in kwargs.items():
            setattr(self, key, value)


    def on_enable(self):
        self.button_dict = {}

        try:
            dirs = os.listdir("saves/")
        except:
            dirs = []

        for dir in dirs:
            if not os.path.exists(f"saves/{dir}/data.json"):
                continue


            def load_world_func():
                self.game.ui_state_handler.state = "None"
                self.game.chunk_handler.enable()
                self.game.chunk_handler.load_world(dir)
                self.game.debug_screen.enable()
                self.game.player.enable()
                mouse.locked = True

            self.button_dict[dir] = Func(load_world_func)

        self.menu_buttons = ButtonList(self.button_dict, y=0, parent=self)


    def on_disable(self):
        destroy(self.menu_buttons)


class PauseMenu(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game


        def continue_func():
            self.game.ui_state_handler.state = "None"
            self.game.player.enable()
            mouse.locked = True

        self.continue_button = Button(parent=self,
                                      text="Continue Playing",
                                      position=Vec2(0, .05),
                                      scale=Vec2(.25, .075),
                                      on_click=Func(continue_func))


        def unload_world_func():
            self.game.ui_state_handler.state = "main_menu"
            self.game.chunk_handler.unload_world()
            self.game.chunk_handler.disable()
            self.game.debug_screen.disable()
            self.game.player.disable()
            mouse.locked = False

        self.leave_button = Button(parent=self,
                                   text="Leave World",
                                   position=Vec2(0, -.05),
                                   scale=Vec2(.25, .075),
                                   on_click=Func(unload_world_func))

        for key, value in kwargs.items():
            setattr(self, key, value)


class DebugScreen(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game

        self.position_display = Text(parent=self,
                                     position=window.top_left,
                                     origin=Vec2(-0.5, 0.5),
                                     text="")

        self.rotation_display = Text(parent=self,
                                     position=window.top_left,
                                     origin=Vec2(-0.5, 1.5),
                                     text="")

        self.update_display = Text(parent=self,
                                   position=window.top_left,
                                   origin=Vec2(-0.5, 2.5),
                                   text="")

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.position_display.text = f"{self.game.player.position}"

        self.rotation_display.text = f"{round(self.game.player.rotation[1], 5)}, {round(self.game.player.camera_pivot.rotation[0], 5)}"

        self.update_display.text = f"{self.game.chunk_handler.updating}"
