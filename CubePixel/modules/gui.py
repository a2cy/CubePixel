import os
import ursina

from ursina.prefabs.health_bar import HealthBar


class MainMenu(ursina.Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__(parent=ursina.camera.ui)

        self.background = ursina.Entity(parent=self,
                                        model="quad",
                                        texture="shore",
                                        scale=ursina.camera.aspect_ratio)

        self.exit_button = ursina.Button(parent=self,
                                         text="X",
                                         position=ursina.window.top_right,
                                         origin=ursina.Vec2(.8, .8),
                                         scale=ursina.Vec2(.03, .03),
                                         on_click=ursina.Func(ursina.application.quit))

        self.world_name_input = ursina.InputField(parent=self,
                                                  position=ursina.Vec2(0, .3))

        self.world_seed_input = ursina.InputField(parent=self,
                                                  position=ursina.Vec2(0, .2),
                                                  limit_content_to='0123456789')
        self.world_name_input.next_field = self.world_seed_input

        self.world_name_text = ursina.Text(parent=self,
                                           text="World Name",
                                           position=ursina.Vec2(0, .34),
                                           origin=ursina.Vec2(0, 0))

        self.world_seed_text = ursina.Text(parent=self,
                                           text="World Seed",
                                           position=ursina.Vec2(0, .24),
                                           origin=ursina.Vec2(0, 0))


        def create_world_func():
            world_name = self.world_name_input.text.lower()
            world_seed = self.world_seed_input.text
            if not world_name or os.path.exists(f"./saves/{world_name}/"):
                return

            if not world_seed:
                world_seed = round(ursina.time.time())
            
            self.world_name_input.text = ""
            self.world_seed_input.text = ""

            self.game.ui_state_handler.state = "loading_screen"
            self.game.chunk_handler.enable()
            self.game.chunk_handler.create_world(world_name, int(world_seed))
            self.game.debug_screen.enable()
            self.game.player.enable()
            ursina.mouse.locked = True

        self.new_world = ursina.Button(parent=self,
                                       text="New World",
                                       position=ursina.Vec2(.4, .25),
                                       scale=ursina.Vec2(.25, .075),
                                       on_click=ursina.Func(create_world_func))

        for key, value in kwargs.items():
            setattr(self, key, value)


    def on_enable(self):
        if os.path.exists("./saves/"):

            self.button_dict = {}

            for file in os.listdir("./saves/"):

                def load_world_func():
                    self.game.ui_state_handler.state = "loading_screen"
                    self.game.chunk_handler.enable()
                    self.game.chunk_handler.load_world(file)
                    self.game.debug_screen.enable()
                    self.game.player.enable()
                    ursina.mouse.locked = True

                self.button_dict[file] = ursina.Func(load_world_func)

            self.menu_buttons = ursina.ButtonList(self.button_dict, y=0, parent=self)


    def on_disable(self):
        try:
            ursina.destroy(self.menu_buttons)
        except Exception as exception:
            print(exception)


class LoadingScreen(ursina.Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=ursina.camera.ui)
        self.game = game

        self.background = ursina.Entity(parent=self,
                                        model="quad",
                                        texture="shore",
                                        scale=ursina.camera.aspect_ratio)

        self.loading_bar = HealthBar(parent=self,
                                     value=0,
                                     position=ursina.Vec2(ursina.window.center[0]-.25, ursina.window.center[1]+.025),
                                     animation_duration=0,
                                     show_lines=False,
                                     bar_color=ursina.color.gray)

        for key, value in kwargs.items():
            setattr(self, key, value)

    
    def update(self):
        self.loading_bar.value = round(self.game.chunk_handler.update_percentage)

        if round(self.game.chunk_handler.update_percentage) == 100:
            self.game.ui_state_handler.state = "None"


class PauseMenu(ursina.Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=ursina.camera.ui)
        self.game = game


        def continue_func():
            self.game.ui_state_handler.state = "None"
            self.game.player.enable()
            ursina.mouse.locked = True

        self.continue_button = ursina.Button(parent=self,
                                             text="Continue Playing",
                                             position=ursina.Vec2(0, .05),
                                             scale=ursina.Vec2(.25, .075),
                                             on_click=ursina.Func(continue_func))


        def unload_world_func():
            self.game.ui_state_handler.state = "main_menu"
            self.game.chunk_handler.unload_world()
            self.game.chunk_handler.disable()
            self.game.debug_screen.disable()
            self.game.player.disable()
            ursina.mouse.locked = False

        self.leave_button = ursina.Button(parent=self,
                                          text="Leave World",
                                          position=ursina.Vec2(0, -.05),
                                          scale=ursina.Vec2(.25, .075),
                                          on_click=ursina.Func(unload_world_func))

        for key, value in kwargs.items():
            setattr(self, key, value)


class DebugScreen(ursina.Entity):

    def __init__(self, game, **kwargs):
        super().__init__(parent=ursina.camera.ui)
        self.game = game

        self.position_display = ursina.Text(parent=self,
                                            position=ursina.window.top_left,
                                            origin=ursina.Vec2(-0.5, 0.5),
                                            text="")

        self.rotation_display = ursina.Text(parent=self,
                                            position=ursina.window.top_left,
                                            origin=ursina.Vec2(-0.5, 1.5),
                                            text="")

        self.update_percentage_display = ursina.Text(parent=self,
                                                     position=ursina.window.top_left,
                                                     origin=ursina.Vec2(-0.5, 2.5),
                                                     text="")

        self.update_display = ursina.Text(parent=self,
                                          position=ursina.window.top_left,
                                          origin=ursina.Vec2(-0.5, 3.5),
                                          text="")

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.position_display.text = f"{self.game.player.position}"

        self.rotation_display.text = f"{round(self.game.player.rotation[1], 5)}, {round(self.game.player.camera_pivot.rotation[0], 5)}"

        self.update_percentage_display.text = f"{round(self.game.chunk_handler.update_percentage)}%"

        self.update_display.text = f"{self.game.chunk_handler.updating}"
