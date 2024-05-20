from ursina import Entity, Text, Mesh, Func, Animator, Vec2, Sky, application, color, time, Quad, camera, scene, window

from src.gui_prefabs import MenuButton, MenuContent, InputField, Button, FileBrowser


class Gui(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sky = Sky(parent=scene)

        self.main_menu = MainMenu()

        self.pause_menu = PauseMenu()

        self.loading_menu = LoadingMenu()

        self.ui_state = Animator({"": None,
                                  "main_menu": self.main_menu,
                                  "pause_menu": self.pause_menu,
                                  "loading_menu": self.loading_menu},
                                  "main_menu")


    def input(self, key):
        from src.player import instance as player

        if self.ui_state.state == "" and key == "escape":
            self.ui_state.state = "pause_menu"
            player.disable()

        elif self.ui_state.state == "pause_menu" and key == "escape":
            self.ui_state.state = ""
            player.enable()


    def update(self):
        self.sky.position = camera.position


class MainMenu(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 scale=window.aspect_ratio,
                                 z=2)

        self.background_panel = Entity(parent=self,
                                       model="quad",
                                       color=color.black66,
                                       position=window.left+Vec2(.25, 0),
                                       scale=Vec2(.4, 1),
                                       z=1)

        self.panel_overlay = Entity(parent=self,
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

        self.world_creation = WorldCreation(parent=self)

        self.world_loading = WorldLoading(parent=self)

        self.options = Options(parent=self)

        self.content_state = Animator({"": None,
                                       "world_creation": self.world_creation,
                                       "world_loading": self.world_loading,
                                       "options": self.options},
                                       "world_creation")

        self.create_button = MenuButton(parent=self, text="Create World", position=window.left+Vec2(.25, .35),
                                        on_click=Func(setattr, self.content_state, "state", "world_creation"))

        self.load_button = MenuButton(parent=self, text="Load World", position=window.left+Vec2(.25, .25),
                                      on_click=Func(setattr, self.content_state, "state", "world_loading"))

        self.options_button = MenuButton(parent=self, text="Options", position=window.left+Vec2(.25, .15),
                                         on_click=Func(setattr, self.content_state, "state", "options"))

        self.exit_button = MenuButton(parent=self, text="Exit", position=window.left+Vec2(.25, .05), on_click=Func(application.quit))


    def on_enable(self):
        for child in self.children:
            if hasattr(child, "on_enable"):
                child.on_enable()

        self.content_state.state = "world_creation"


class PauseMenu(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.background_panel = Entity(parent=self,
                                       model="quad",
                                       color=color.black66,
                                       position=window.left+Vec2(.25, 0),
                                       scale=Vec2(.4, 1),
                                       z=1)

        self.panel_overlay = Entity(parent=self,
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

        self.options = Options(parent=self)


        def _continue():
            from src.player import instance as player

            instance.ui_state.state = "loading_menu"
            player.enable()


        self.continue_button = MenuButton(parent=self, text="Continue Playing", position=window.left+Vec2(.25, .35),
                                          on_click=_continue)


        def _return():
            from src.chunk_handler import instance as chunk_handler

            instance.ui_state.state = "main_menu"
            chunk_handler.unload_world()

        self.return_button = MenuButton(parent=self, text="Return To Menu", position=window.left+Vec2(.25, .25),
                                        on_click=_return)


    def on_enable(self):
        for child in self.children:
            if hasattr(child, "on_enable"):
                child.on_enable()


class LoadingMenu(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.background = Entity(parent=self,
                                 model="quad",
                                 texture="shore",
                                 scale=window.aspect_ratio,
                                 z=2)

        self.background_panel = Entity(parent=self,
                                        model=Quad(aspect=.25 / .15, radius=.1),
                                        color=color.black66,
                                        scale=Vec2(.25, .2),
                                        z=1)

        self.title = Text(parent=self,
                          text="Loading ...",
                          scale=1.8,
                          position=Vec2(0, .03),
                          origin=Vec2(0, 0))

        self.status = Text(parent=self,
                          text="",
                          scale=0.8,
                          position=Vec2(0, -.035),
                          origin=Vec2(0, 0))


    def update(self):
        from src.chunk_handler import instance as chunk_handler

        self.status.text = chunk_handler.loading_state


class WorldCreation(MenuContent):

    def __init__(self, **kwargs):
        super().__init__("Create World", **kwargs)

        self.world_name = InputField(parent=self, position=window.right+Vec2(-.65, .3))

        self.world_name_label = Text(parent=self,
                                     text="World Name",
                                     scale=1.2,
                                     position=self.world_name.position+Vec2(-.5, 0),
                                     origin=Vec2(-.5, 0))

        self.world_seed = InputField(parent=self, position=window.right+Vec2(-.65, .2), limit_content_to='0123456789')

        self.world_seed_label = Text(parent=self,
                                     text="World Seed",
                                     scale=1.2,
                                     position=self.world_seed.position+Vec2(-.5, 0),
                                     origin=Vec2(-.5, 0))


        def create_world():
            from src.player import instance as player
            from src.chunk_handler import instance as chunk_handler

            if not self.world_name.text:
                print("error")
                return

            seed = int(self.world_seed.text) if self.world_seed.text else int(time.time())

            if chunk_handler.create_world(self.world_name.text, seed):
                print("error")
                return

            instance.ui_state.state = ""
            player.enable()

        self.create_button = Button(parent=self, text="Create World", position=window.right+Vec2(-.65, 0),
                                    on_click=create_world)

        self.world_name.next_field = self.world_seed


    def on_enable(self):
        self.world_name.text = ""
        self.world_seed.text = ""


class WorldLoading(MenuContent):

    def __init__(self, **kwargs):
        super().__init__("Load World", **kwargs)

        self.file_browser = FileBrowser(parent=self, position=window.right+Vec2(-.65, .4), start_path="./saves/")


        def load_world():
            from src.player import instance as player
            from src.chunk_handler import instance as chunk_handler

            if not self.file_browser.selection:
                print("error")
                return

            try:
                chunk_handler.load_world(self.file_browser.selection[0])
            except:
                print("error")
                return

            instance.ui_state.state = "loading_menu"
            player.enable()

        self.load_button = Button(parent=self, text="Load World", position=window.right+Vec2(-.9, -0.4),
                                  on_click=load_world)


        def rename_world():
            if not self.file_browser.selection:
                print("error")
                return

        self.rename_button = Button(parent=self, text="Rename World", position=window.right+Vec2(-.65, -0.4),
                                    on_click=rename_world)


        def delete_world():
            if not self.file_browser.selection:
                print("error")
                return

        self.delete_button = Button(parent=self, text="Delete World", position=window.right+Vec2(-.4, -0.4),
                                    on_click=delete_world)


    def on_enable(self):
        self.file_browser.on_enable()


class Options(MenuContent):

    def __init__(self, **kwargs):
        super().__init__("Options", **kwargs)

instance = Gui()
