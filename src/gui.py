from ursina import Entity, Text, Mesh, Func, Animator, Sequence, InputField, Vec2, application, color, camera, window

from src.gui_prefabs import MenuButton, MenuPanel


class Gui(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.main_menu = MainMenu(self.game)

        self.pause_menu = PauseMenu(self.game)

        self.ui_state = Animator({"": None,
                                       "main_menu": self.main_menu,
                                       "pause_menu": self.pause_menu},
                                       "main_menu")


    def input(self, key):
        if self.game.chunk_handler.world_loaded and key == "escape":
            self.game.player.disable()
            self.ui_state.state = "pause_menu"


class MainMenu(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__(parent=camera.ui)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 scale=window.aspect_ratio,
                                 z=2)

        self.button_background = Entity(parent=self,
                                        model="quad",
                                        color=color.black66,
                                        position=window.left+Vec2(.25, 0),
                                        scale=Vec2(.4, 1),
                                        z=1)

        self.button_overlay = Entity(parent=self,
                                     model=Mesh(vertices=[(.5,-.5,0), (.5,.8,0), (-.5,.8,0), (-.5,-.5,0)], mode="line", thickness=2),
                                     color=color.black90,
                                     position=window.left+Vec2(.25, 0),
                                     scale=Vec2(.4, 1),
                                     z=1)

        self.title = Text(parent=self,
                          text="CubePixel",
                          scale=1.8,
                          position=window.left+Vec2(.25, .45),
                          origin=Vec2(0, 0))

        self.world_creation = WorldCreation(self.game, parent=self)

        self.world_loading = WorldLoading(self.game, parent=self)

        self.options = Options(self.game, parent=self)

        self.context_state = Animator({"": None,
                                       "world_creation": self.world_creation,
                                       "world_loading": self.world_loading,
                                       "options": self.options},
                                       "world_creation")

        self.create_button = MenuButton(parent=self, text="Create World", position=window.left+Vec2(.25, .35),
                                        on_click=Sequence(Func(setattr, self.context_state, "state", "world_creation")))

        self.load_button = MenuButton(parent=self, text="Load World", position=window.left+Vec2(.25, .25),
                                      on_click=Sequence(Func(setattr, self.context_state, "state", "world_loading")))

        self.options_button = MenuButton(parent=self, text="Options", position=window.left+Vec2(.25, .15),
                                         on_click=Sequence(Func(setattr, self.context_state, "state", "options")))

        self.exit_button = MenuButton(parent=self, text="Exit", position=window.left+Vec2(.25, .05), on_click=Func(application.quit))


class PauseMenu(Entity):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__(parent=camera.ui)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.button_background = Entity(parent=self,
                                        model="quad",
                                        color=color.black66,
                                        position=window.left+Vec2(.25, 0),
                                        scale=Vec2(.4, 1),
                                        z=1)

        self.button_overlay = Entity(parent=self,
                                     model=Mesh(vertices=[(.5,-.5,0), (.5,.8,0), (-.5,.8,0), (-.5,-.5,0)], mode="line", thickness=2),
                                     color=color.black90,
                                     position=window.left+Vec2(.25, 0),
                                     scale=Vec2(.4, 1),
                                     z=1)

        self.title = Text(parent=self,
                          text="CubePixel",
                          scale=1.8,
                          position=window.left+Vec2(.25, .45),
                          origin=Vec2(0, 0))

        self.options = Options(self.game, parent=self)

        self.continue_button = MenuButton(parent=self, text="Continue Playing", position=window.left+Vec2(.25, .35),
                                          on_click=Sequence(Func(lambda: setattr(getattr(self.game, "gui").ui_state, "state", "")),
                                                            Func(lambda: getattr(self.game, "player").enable())))

        self.return_button = MenuButton(parent=self, text="Return To Menu", position=window.left+Vec2(.25, .25),
                                        on_click=Sequence(Func(lambda: setattr(getattr(self.game, "gui").ui_state, "state", "main_menu")),
                                                          Func(lambda: getattr(self.game, "chunk_handler").unload_world())))


class WorldCreation(MenuPanel):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__("Create World")

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.word_name = InputField(parent=self, position=window.right+Vec2(-.65, .3))

        self.word_name_label = Text(parent=self,
                                text="World Name",
                                scale=1.2,
                                position=self.word_name.position+Vec2(-.5, 0),
                                origin=Vec2(-.5, 0))

        self.word_seed = InputField(parent=self, position=window.right+Vec2(-.65, .2), limit_content_to='0123456789')

        self.word_seed_label = Text(parent=self,
                                text="World Seed",
                                scale=1.2,
                                position=self.word_seed.position+Vec2(-.5, 0),
                                origin=Vec2(-.5, 0))

        self.create_button = MenuButton(parent=self, text="Create World", position=window.right+Vec2(-.65, 0),
                                        on_click=Sequence(Func(lambda: getattr(self.game, "chunk_handler").create_world(self.word_name.text, int(self.word_seed.text))),
                                                          Func(lambda: setattr(getattr(self.game, "gui").ui_state, "state", "")),
                                                          Func(lambda: getattr(self.game, "player").enable())))

        self.word_name.next_field = self.word_seed


    def on_disable(self):
        self.word_name.text = ""
        self.word_seed.text = ""


class WorldLoading(MenuPanel):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__("Load World")

        for key, value in kwargs.items():
            setattr(self, key, value)


class Options(MenuPanel):

    def __init__(self, game, **kwargs):
        self.game = game
        super().__init__("Options")

        for key, value in kwargs.items():
            setattr(self, key, value)