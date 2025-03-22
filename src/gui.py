from ursina import Entity, Text, Slider, CheckBox, Mesh, Func, Animator, Vec2, color, time, camera, window

from src.gui_prefabs import MenuButton, MenuContent, InputField, ButtonPrefab, FileButton, ItemButton
from src.resource_loader import instance as resource_loader
from src.chunk_manager import instance as chunk_manager
from src.player import instance as player
from src.settings import instance as settings


class Gui(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from ursina import Sky, scene

        self.sky = Sky(parent=scene)
        self.sky.disable()

        self.main_menu = MainMenu()

        self.pause_menu = PauseMenu()

        self.inventory = Inventory()

        self.loading_menu = LoadingMenu()

        self.debug_overlay = DebugOverlay(enabled=False)

        self.ui_state = Animator({"": None,
                                  "main_menu": self.main_menu,
                                  "pause_menu": self.pause_menu,
                                  "inventory": self.inventory,
                                  "loading_menu": self.loading_menu},
                                  "main_menu")


    def input(self, key):
        if self.ui_state.state == "" and key == "escape":
            self.ui_state.state = "pause_menu"
            player.disable()

        elif self.ui_state.state == "pause_menu" and key == "escape":
            self.ui_state.state = ""
            player.enable()

        if self.ui_state.state == "" and key == "tab":
            self.ui_state.state = "inventory"
            player.disable()

        elif self.ui_state.state == "inventory" and (key == "tab" or key == "escape"):
            self.ui_state.state = ""
            player.enable()


    def update(self):
        self.sky.position = camera.world_position


class MainMenu(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        from ursina import application

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

        self.exit_button = MenuButton(parent=self, text="Exit", position=window.left+Vec2(.25, .05),
                                      on_click=Func(application.quit))


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
            instance.ui_state.state = ""
            player.enable()


        self.continue_button = MenuButton(parent=self, text="Continue Playing", position=window.left+Vec2(.25, .35),
                                          on_click=_continue)

        def _return():
            instance.ui_state.state = "main_menu"
            chunk_manager.unload_world()
            instance.sky.disable()


        self.return_button = MenuButton(parent=self, text="Return To Menu", position=window.left+Vec2(.25, .25),
                                        on_click=_return)


    def on_enable(self):
        for child in self.children:
            if hasattr(child, "on_enable"):
                child.on_enable()


class Inventory(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        self.max_buttons = 9
        self.button_parent = Entity(parent=self, z=-1)

        self.background_panel = Entity(parent=self,
                                       model="quad",
                                       color=color.black66,
                                       scale=Vec2(1, 1),
                                       z=1)

        self.panel_overlay = Entity(parent=self,
                                    model=Mesh(vertices=[(.5,-.5,0), (.5,.8,0), (-.5,.8,0), (-.5,-.5,0)], mode="line", thickness=2),
                                    color=color.black90,
                                    scale=Vec2(1, 1),
                                    z=1)

        button_count = 0
        for i, voxel in enumerate(resource_loader.voxel_types):
            if not voxel.inventory:
                continue

            ItemButton(parent=self.button_parent,
                       x=(button_count % self.max_buttons) * .1 - .4,
                       y=-(button_count // self.max_buttons) * .1 + .4,
                       voxel_id=i+1)

            button_count += 1


    @property
    def selection(self):
        return [c.voxel_id for c in self.button_parent.children if c.selected == True]


class LoadingMenu(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        from ursina import Quad

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
        if chunk_manager.finished_loading:
            instance.ui_state.state = ""

        self.indicator.rotation_z += 150 * time.dt


    def on_disable(self):
        if chunk_manager.world_loaded:
            player.enable()
            instance.sky.enable()


class Notification(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        from ursina import Quad

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


class DebugOverlay(Entity):

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=2, **kwargs)

        self.coordinates = Text(parent=self, position=window.top_left)
        self.direction = Text(parent=self, position=window.top_left + Vec2(0, -.03))


    def update(self):
        rotation = player.rotation_y
        heading = "none"

        if rotation < 0:
            rotation += 360

        if rotation > 315 or rotation < 45:
            heading = "north z+"

        if rotation > 45 and rotation < 135:
            heading = "east x+"

        if rotation > 135 and rotation < 225:
            heading = "south z-"

        if rotation > 225 and rotation < 315:
            heading = "west x-"

        self.coordinates.text = f"position : {round(player.position.x)}  {round(player.position.y)}  {round(player.position.z)}"
        self.direction.text = f"facing : {heading}"


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


        self.create_button = ButtonPrefab(parent=self, text="Create World", position=window.right+Vec2(-.65, 0),
                                    on_click=create_world)

        self.world_name.next_field = self.world_seed


    def on_enable(self):
        self.world_name.text = ""
        self.world_seed.text = ""


class WorldLoading(MenuContent):

    def __init__(self, **kwargs):
        super().__init__("Load World", **kwargs)

        self.max_buttons = 11
        self.button_parent = Entity(parent=self, position=window.right+Vec2(-.65, 0))

        self.scroll_up = Entity(parent=self, model="quad", texture="arrow_down", scale=.08, rotation_z=180, position=window.right+Vec2(-.35, .35))
        self.scroll_down = Entity(parent=self, model="quad", texture="arrow_down", scale=.08, position=window.right+Vec2(-.35, -.3))

        def load_world():
            if not self.selection:
                instance.main_menu.notification.notify("No world selected")
                return

            try:
                chunk_manager.load_world(self.selection[0])
            except:
                instance.main_menu.notification.notify("Failed to load world")
                return

            instance.ui_state.state = "loading_menu"


        self.load_button = ButtonPrefab(parent=self, text="Load World", position=window.right+Vec2(-.9, -.4),
                                  on_click=load_world)

        def delete_world():
            if not self.selection:
                instance.main_menu.notification.notify("No world selected")
                return

            try:
                chunk_manager.delete_world(self.selection[0])
            except:
                instance.main_menu.notification.notify("Failed to delete world")
                return

            self.on_enable()


        self.delete_button = ButtonPrefab(parent=self, text="Delete World", position=window.right+Vec2(-.4, -.4),
                                    on_click=delete_world)


    @property
    def scroll(self):
        return self._scroll

    @scroll.setter
    def scroll(self, value):
        self._scroll = value

        for i, c in enumerate(self.button_parent.children):
            if i < value or i >= value + self.max_buttons:
                c.enabled = False
            else:
                c.enabled = True

        self.scroll_up.enabled = value > 0
        self.scroll_down.enabled = self.max_buttons < len(self.button_parent.children) and \
                                   value < len(self.button_parent.children) - self.max_buttons

        self.button_parent.y = value * .055


    @property
    def selection(self):
        return [c.path for c in self.button_parent.children if c.selected == True]


    def input(self, key):
        if key == 'scroll down':
            if self.scroll + self.max_buttons < len(self.button_parent.children):
                self.scroll += 1

        if key == 'scroll up':
            if self.scroll > 0:
                self.scroll -= 1


    def on_enable(self):
        import os
        from ursina import destroy

        self.scroll = 0

        for i in range(len(self.button_parent.children)):
            destroy(self.button_parent.children.pop())

        if not os.path.exists("./saves/"):
            return

        files = os.listdir("./saves/")
        files.sort()

        for i, file in enumerate(files):
            prefix = ' <light_gray>'

            FileButton(parent=self.button_parent, path=file, text=prefix+file, y=-i*.055 +.3, add_to_scene_entities=False)


class Options(MenuContent):

    def __init__(self, **kwargs):
        super().__init__("Options", **kwargs)

        self.render_distance_label = Text(parent=self,
                                          text="Render Distance",
                                          scale=1.2,
                                          position=Vec2(-.2, .3),
                                          origin=Vec2(0, 0))

        self.render_distance = Slider(parent=self, position=self.render_distance_label.position+Vec2(.2, 0), min=2, max=8, step=1)

        def render_distance_setter():
            settings.settings["render_distance"] = self.render_distance.value
            settings.save_settings()

            chunk_manager.reload()


        self.render_distance.on_value_changed = render_distance_setter

        self.chunk_updates_label = Text(parent=self,
                                          text="Chunk Updates",
                                          scale=1.2,
                                          position=Vec2(-.2, .22),
                                          origin=Vec2(0, 0))

        self.chunk_updates = Slider(parent=self, position=self.chunk_updates_label.position+Vec2(.2, 0), min=1, max=8, step=1)

        def chunk_updates_setter():
            settings.settings["chunk_updates"] = self.chunk_updates.value
            settings.save_settings()

            chunk_manager.reload()


        self.chunk_updates.on_value_changed = chunk_updates_setter

        self.mouse_sensitivity_label = Text(parent=self,
                                            text="Mouse Sensitivity",
                                            scale=1.2,
                                            position=Vec2(-.2, .14),
                                            origin=Vec2(0, 0))

        self.mouse_sensitivity = Slider(parent=self, position=self.mouse_sensitivity_label.position+Vec2(.2, 0), min=60, max=120, step=1)

        def mouse_sensitivity_setter():
            settings.settings["mouse_sensitivity"] = self.mouse_sensitivity.value
            settings.save_settings()

            player.reload()


        self.mouse_sensitivity.on_value_changed = mouse_sensitivity_setter

        self.fov_label = Text(parent=self,
                              text="Fov",
                              scale=1.2,
                              position=Vec2(-.2, .06),
                              origin=Vec2(0, 0))

        self.fov = Slider(parent=self, position=self.fov_label.position+Vec2(.2, 0), min=60, max=120, dynamic=True, step=1)

        def fov_setter():
            settings.settings["fov"] = self.fov.value
            settings.save_settings()

            player.reload()


        self.fov.on_value_changed = fov_setter

        self.debug_label = Text(parent=self,
                              text="Debug Overlay",
                              scale=1.2,
                              position=Vec2(-.2, -.02),
                              origin=Vec2(0, 0))

        self.debug_toggle = CheckBox(parent=self, position=self.debug_label.position+Vec2(.2, 0), start_value=False)

        def toggle_debug():
            self.debug_toggle.value = not self.debug_toggle.value

            instance.debug_overlay.enabled = self.debug_toggle.value


        self.debug_toggle.on_click = toggle_debug

        from ursina import Button, Tooltip

        info_text ="""  w,a,s,d - movement

  space - jump

  shift - sprint

  n - toggle noclip mode

  e,q - noclip up / down

  tab - inventory

  L mouse - break voxel

  R mouse - place voxel"""

        self.controls = Button(parent=self,
                               model='circle',
                               text='?',
                               position=window.bottom_right+Vec2(-.085, .03),
                               scale=.025,
                               tooltip=Tooltip(info_text, scale=.75))


    def on_enable(self):
        self.render_distance.value = settings.settings["render_distance"]
        self.chunk_updates.value = settings.settings["chunk_updates"]
        self.mouse_sensitivity.value = settings.settings["mouse_sensitivity"]
        self.fov.value = settings.settings["fov"]


instance = Gui()