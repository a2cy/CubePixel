from ursina import Entity, Text, Slider, Mesh, Func, Animator, Vec2, Sky, application, color, time, Quad, camera, scene, window

from src.gui_prefabs import MenuButton, MenuContent, InputField, Button, FileBrowser
from src.settings import instance as settings


class Gui(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sky = Sky(parent=scene)
        self.sky.disable()

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
        self.sky.position = camera.world_position


class Notification(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.idle_position = window.left+Vec2(-.25, -.4)
        self.active_position = window.left+Vec2(.25, -.4)

        self.model = Quad(aspect=.35 / .1)
        self.color = color.black50
        self.scale = Vec2(.35, .1)
        self.position = self.idle_position

        self.text = Text(parent=self, text="", z=-.1, scale=Vec2(1/self.scale.x, 1/self.scale.y), origin=Vec2(0, 0), color=color.yellow)

        self.cooldown = 0


    def update(self):
        if self.cooldown > 0:
            self.cooldown -= time.dt
            return

        if self.position.xy == self.active_position:
            self.animate_position(self.idle_position, duration=.25)
            self.cooldown = .5


    def notify(self, text):
        self.animate_position(self.active_position, duration=.25)
        self.text.text = text
        self.cooldown = 2


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

        self.notification = Notification()

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

            instance.ui_state.state = ""
            player.enable()


        self.continue_button = MenuButton(parent=self, text="Continue Playing", position=window.left+Vec2(.25, .35),
                                          on_click=_continue)

        def _return():
            from src.chunk_manager import instance as chunk_manager

            instance.ui_state.state = "main_menu"
            chunk_manager.unload_world()
            instance.sky.disable()


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
                                        model=Quad(aspect=.25 / .2, radius=.1),
                                        color=color.black66,
                                        scale=Vec2(.25, .2),
                                        z=1)

        self.title = Text(parent=self,
                          text="Loading ...",
                          scale=1.8,
                          position=Vec2(0, .03),
                          origin=Vec2(0, 0))

        self.indicator = Entity(parent=self,
                             model="quad",
                             texture="cog",
                             scale=.05,
                             position=Vec2(0, -.04))


    def update(self):
        from src.chunk_manager import instance as chunk_manager

        if chunk_manager.finished_loading:
            instance.ui_state.state = ""

        self.indicator.rotation_z += 2


    def on_disable(self):
        from src.player import instance as player
        from src.chunk_manager import instance as chunk_manager

        if chunk_manager.world_loaded:
            player.enable()
            instance.sky.enable()


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
            from src.chunk_manager import instance as chunk_manager

            if not self.world_name.text:
                instance.main_menu.notification.notify("Missing world name")
                return

            seed = int(self.world_seed.text) if self.world_seed.text else int(time.time())

            try:
                chunk_manager.create_world(self.world_name.text, seed)
            except:
                instance.main_menu.notification.notify("World name already used")
                return

            instance.ui_state.state = "loading_menu"


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
            from src.chunk_manager import instance as chunk_manager

            if not self.file_browser.selection:
                instance.main_menu.notification.notify("No world selected")
                return

            try:
                chunk_manager.load_world(self.file_browser.selection[0])
            except:
                instance.main_menu.notification.notify("Failed to load world")
                return

            instance.ui_state.state = "loading_menu"


        self.load_button = Button(parent=self, text="Load World", position=window.right+Vec2(-.9, -0.4),
                                  on_click=load_world)

        def delete_world():
            from src.chunk_manager import instance as chunk_manager

            if not self.file_browser.selection:
                instance.main_menu.notification.notify("No world selected")
                return

            try:
                chunk_manager.delete_world(self.file_browser.selection[0])
            except:
                instance.main_menu.notification.notify("Failed to delete world")
                return

            self.file_browser.on_enable()


        self.delete_button = Button(parent=self, text="Delete World", position=window.right+Vec2(-.4, -0.4),
                                    on_click=delete_world)


    def on_enable(self):
        self.file_browser.on_enable()


class Options(MenuContent):

    def __init__(self, **kwargs):
        super().__init__("Options", **kwargs)

        self.render_distance = Slider(parent=self, position=Vec2(0, .3), min=1, max=8, step=1)

        self.render_distance_label = Text(parent=self,
                                          text="Render Distance",
                                          scale=1.2,
                                          position=self.render_distance.position+Vec2(-.2, 0),
                                          origin=Vec2(0, 0))

        def render_distance_setter():
            from src.chunk_manager import instance as chunk_handeler

            settings.settings["render_distance"] = self.render_distance.value
            settings.save_settings()

            chunk_handeler.reload()


        self.render_distance.on_value_changed = render_distance_setter

        self.mouse_sensitivity = Slider(parent=self, position=Vec2(0, .22), min=60, max=120, step=1)

        self.mouse_sensitivity_label = Text(parent=self,
                                            text="Mouse Sensitivity",
                                            scale=1.2,
                                            position=self.mouse_sensitivity.position+Vec2(-.2, 0),
                                            origin=Vec2(0, 0))

        def mouse_sensitivity_setter():
            from src.player import instance as player

            settings.settings["mouse_sensitivity"] = self.mouse_sensitivity.value
            settings.save_settings()

            player.reload()


        self.mouse_sensitivity.on_value_changed = mouse_sensitivity_setter

        self.fov = Slider(parent=self, position=Vec2(0, .14), min=60, max=120, dynamic=True, step=1)

        self.fov_label = Text(parent=self,
                              text="Fov",
                              scale=1.2,
                              position=self.fov.position+Vec2(-.2, 0),
                              origin=Vec2(0, 0))

        def fov_setter():
            from src.player import instance as player

            settings.settings["fov"] = self.fov.value
            settings.save_settings()

            player.reload()

        self.controls = Text(parent=self,
                             text="""
                             w,a,s,d - movement

                             n - toggle noclip mode

                             e,q - noclip up / down

                             space - jump

                             shift - sprint
                             """,
                             scale=1.2,
                             position=Vec2(.12, -.15),
                             origin=Vec2(0, 0))


        self.fov.on_value_changed = fov_setter


    def on_enable(self):
        self.render_distance.value = settings.settings["render_distance"]
        self.mouse_sensitivity.value = settings.settings["mouse_sensitivity"]
        self.fov.value = settings.settings["fov"]

instance = Gui()
