import os

from ursina import Entity, Button, Text, Func, InputField, ButtonList, Vec3, Vec2, application, color, time, window, camera, destroy, invoke
from ursina.models.procedural.quad import Quad


class ExitMenu(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__(parent=camera.ui)

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 z=2)

        self.panel = Entity(parent=self,
                            model=Quad(aspect=.35 / .25),
                            color=color.black66,
                            scale=Vec2(.35, .25))

        self.exit_text = Text(parent=self,
                              text="Are you sure you want to exit?",
                              position=Vec2(0, .05),
                              origin=Vec2(0, 0),
                              wordwrap=20,
                              z=-1)

        self.exit_button = Button(parent=self,
                                  text="Exit",
                                  position=Vec2(-.08, -.05),
                                  scale=Vec2(.1, .075),
                                  on_click=Func(application.quit),
                                  z=-1)

        def cancel_function():
            self.game.ui_state_handler.state = "main_menu"


        self.cancel_button = Button(parent=self,
                                    text="Cancel",
                                    position=Vec2(.08, -.05),
                                    scale=Vec2(.1, .075),
                                    on_click=Func(cancel_function),
                                    z=-1)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.background.scale = window.aspect_ratio


class MainMenu(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__(parent=camera.ui)

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 z=2)

        self.exit_text = Text(parent=self,
                                  text="press escape to exit",
                                  position=window.bottom_right,
                                  origin=Vec2(.6, -.8))

        self.error_text = Text(parent=self,
                               position=window.bottom_left,
                               origin=Vec2(-.6, -.8),
                               color=color.red)

        self.error_sequence = None

        self.world_name_input = InputField(parent=self, position=Vec2(0, .3))

        self.world_seed_input = InputField(parent=self,
                                           position=Vec2(0, .2),
                                           limit_content_to="0123456789")

        self.world_name_input.next_field = self.world_seed_input

        self.world_name_text = Text(parent=self,
                                    text="World Name",
                                    position=Vec2(0, .34),
                                    origin=Vec2(0, 0))

        self.world_seed_text = Text(parent=self,
                                    text="World Seed",
                                    position=Vec2(0, .24),
                                    origin=Vec2(0, 0))


        def create_world_func():
            world_name = self.world_name_input.text.lower()
            world_seed = self.world_seed_input.text
            if not world_name:
                self.error_text.text = "world name missing"
                if self.error_sequence:
                    self.error_sequence.kill()

                self.error_sequence = invoke(setattr, self.error_text, "text", "", delay=2)
                return

            if not world_seed:
                world_seed = time.time()

            if not self.game.chunk_handler.create_world(world_name, int(world_seed)):
                self.error_text.text = "world with this name already exists"
                if self.error_sequence:
                    self.error_sequence.kill()

                self.error_sequence = invoke(setattr, self.error_text, "text", "", delay=2)
                return

            self.game.ui_state_handler.state = "loading_screen"
            self.game.debug_screen.enable()
            self.game.player.enable()

            self.world_name_input.text = ""
            self.world_seed_input.text = ""

        self.new_world = Button(parent=self,
                                text="New World",
                                position=Vec2(.4, .25),
                                scale=Vec2(.25, .075),
                                on_click=Func(create_world_func))

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update_button_list(self):
        if hasattr(self, "menu_buttons"):
            destroy(self.menu_buttons)

        if os.path.exists("./saves/"):

            button_dict = {}
            files = os.listdir("./saves/")
            files.sort()

            for file in files:

                def load_world_func(file):
                    if not self.game.chunk_handler.load_world(file):
                        self.error_text.text = "world with this name does not exist"
                        if self.error_sequence:
                            self.error_sequence.kill()

                        self.error_sequence = invoke(setattr, self.error_text, "text", "", delay=2)
                        return

                    self.game.ui_state_handler.state = "loading_screen"
                    self.game.debug_screen.enable()
                    self.game.player.enable()

                button_dict[file] = Func(load_world_func, file)

            self.menu_buttons = ButtonList(button_dict, y=0, parent=self)


    def input(self, key):
        if key == "escape":
            self.game.ui_state_handler.state = "exit_menu"


    def update(self):
        self.background.scale = window.aspect_ratio


    def on_enable(self):
        self.update_button_list()


class LoadingScreen(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 z=2)

        self.loading_indicator = Entity(parent=self,
                                        model="cube",
                                        texture="stone",
                                        scale=0.4
                                        )

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.background.scale = window.aspect_ratio

        self.loading_indicator.rotation -= Vec3(3,5,0)


    def on_enable(self):
        if hasattr(self, "loading_indicator"):
            self.loading_indicator.rotation = Vec3(0, 0, 0)


class PauseMenu(Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui)
        self.game = game


        def continue_func():
            self.game.ui_state_handler.state = "None"
            self.game.player.enable()

        self.continue_button = Button(parent=self,
                                      text="Continue Playing",
                                      position=Vec2(0, .05),
                                      scale=Vec2(.25, .075),
                                      on_click=Func(continue_func))


        def unload_world_func():
            self.game.ui_state_handler.state = "main_menu"
            self.game.chunk_handler.unload_world()
            self.game.debug_screen.disable()
            self.game.player.disable()

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
        self.update_display.text = f"{self.game.chunk_handler.update_thread.is_alive() if hasattr(self.game.chunk_handler, 'update_thread') else False}"
