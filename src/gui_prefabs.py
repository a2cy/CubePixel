import os
from ursina import Entity, Text, Mesh, Vec2, color, destroy, window
from ursina import InputField as uInputField, Button as uButton


class MenuButton(Entity):

    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)

        self.model = "quad"
        self.collider = "box"
        self.scale=Vec2(.3, .08)
        self.color = color.clear


        self.default_color = color.black
        self.highlight_color = color.azure
        self.pressed_color = color.orange

        self.background = Entity(parent=self, model=Mesh(vertices=[(-.4,-.4,0), (.4,-.4,0)], mode="line", thickness=2), color=self.default_color)

        self.text_entity = Text(parent=self, text=text, scale=(self.scale*50).yx, origin=Vec2(0, 0), color=self.default_color, add_to_scene_entities=False)


    def input(self, key):
        if key == 'left mouse down':
            if self.hovered:
                self.background.color = self.pressed_color
                self.text_entity.color = self.pressed_color

        if key == 'left mouse up':
            if self.hovered:
                self.background.color = self.highlight_color
                self.text_entity.color = self.highlight_color

            else:
                self.background.color = self.default_color
                self.text_entity.color = self.default_color


    def on_mouse_enter(self):
        self.background.color = self.highlight_color
        self.text_entity.color = self.highlight_color


    def on_mouse_exit(self):
        self.background.color = self.default_color
        self.text_entity.color = self.default_color


class MenuContent(Entity):

    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)

        self.background_panel = Entity(parent=self,
                                       model="quad",
                                       color=color.black66,
                                       position=window.right+Vec2(-.65, 0),
                                       scale=Vec2(1.2, 1),
                                       z=1)

        self.panel_overlay = Entity(parent=self,
                                    model=Mesh(vertices=[(.5,-.5,0), (.5,.5,0), (-.5,.5,0), (-.5,-.5,0)], mode="line", thickness=2),
                                    color=color.black90,
                                    position=window.right+Vec2(-.65, 0),
                                    scale=Vec2(1.2, 1),
                                    z=1)

        self.label = Text(parent=self,
                          text=text,
                          scale=1.4,
                          position=window.right+Vec2(-.65, .42),
                          origin=Vec2(0, 0))


class InputField(uInputField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = color.black50
        self.highlight_color = color.black66

        self.background = Entity(parent=self, model=Mesh(vertices=[(-.46,-.4,0), (.46,-.4,0)], mode="line", thickness=2), color=self.default_color)


class Button(uButton):

    def __init__(self, **kwargs):
        super().__init__(scale = Vec2(.2, .08), **kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90


class FileButton(uButton):
    def __init__(self, load_menu, path, **kwargs):
        self.load_menu = load_menu
        self.path = path

        super().__init__(scale=(.5,.05), pressed_scale=1, **kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90

        self.text_entity.scale *= 1.2
        self.original_color = self.color
        self.selected = False


    def on_click(self):
        if len([e for e in self.parent.children if e.selected]) >= self.load_menu.selection_limit and not self.selected:
            for e in self.parent.children:
                e.selected = False

        self.selected = not self.selected


    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        if value == True:
            self.color = self.pressed_color
        else:
            self.color = self.original_color


class FileBrowser(Entity):
    def __init__(self, start_path, **kwargs):
        self.start_path = start_path
        super().__init__(**kwargs)

        self.return_files = True
        self.return_folders = False
        self.selection_limit = 1
        self.max_buttons = 12

        self.button_parent = Entity(parent=self)


    def input(self, key):
        if key == 'scroll down':
            if self.scroll + self.max_buttons < len(self.button_parent.children)-1:
                self.scroll += 1

        if key == 'scroll up':
            if self.scroll > 0:
                self.scroll -= 1


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

        self.button_parent.y = value * .055


    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

        for i in range(len(self.button_parent.children)):
            destroy(self.button_parent.children.pop())

        if not os.path.exists(value):
            return

        files = os.listdir(value)
        files.sort()

        for i, file in enumerate(files):
            prefix = ' <light_gray>'

            FileButton(parent=self.button_parent, path=file, text=prefix+file, y=-i*.055 -.09, load_menu=self, add_to_scene_entities=False)

        self.scroll = 0


    @property
    def selection(self):
        return [c.path for c in self.button_parent.children if c.selected == True]


    def on_enable(self):
        self.path = self.start_path
        self.scroll = 0
