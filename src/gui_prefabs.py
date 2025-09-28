from ursina import Entity, Button, Slider, Text, Mesh, Vec2, color, Quad, window
from ursina import InputField as uInputField


class MenuButton(Entity):
    def __init__(self, text="", default_color=color.black, **kwargs):
        super().__init__(**kwargs)

        self.model = "quad"
        self.collider = "box"
        self.scale = Vec2(0.3, 0.08)
        self.color = color.clear

        self.default_color = default_color
        self.highlight_color = color.azure
        self.pressed_color = color.orange

        self.background = Entity(
            parent=self, model=Mesh(vertices=[(-0.4, -0.4, 0), (0.4, -0.4, 0)], mode="line", thickness=2), color=self.default_color
        )

        self.text_entity = Text(
            parent=self, text=text, scale=(self.scale * 50).yx, origin=Vec2(0, 0), color=self.default_color, add_to_scene_entities=False
        )

    def input(self, key):
        if key == "left mouse down":
            if self.hovered:
                self.background.color = self.pressed_color
                self.text_entity.color = self.pressed_color

        if key == "left mouse up":
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

        self.background_panel = Entity(
            parent=self, model="quad", color=color.black50, position=window.right + Vec2(-0.65, 0), scale=Vec2(1.2, 1), z=1
        )

        self.panel_overlay = Entity(
            parent=self,
            model=Mesh(vertices=[(0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0), (-0.5, -0.5, 0)], mode="line", thickness=2),
            color=color.black90,
            position=window.right + Vec2(-0.65, 0),
            scale=Vec2(1.2, 1),
            z=1,
        )

        self.label = Text(parent=self, text=text, scale=1.5, position=window.right + Vec2(-0.65, 0.42), origin=Vec2(0, 0))


class InputField(uInputField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = color.black50
        self.highlight_color = color.black66

        self.background = Entity(
            parent=self, model=Mesh(vertices=[(-0.46, -0.4, 0), (0.46, -0.4, 0)], mode="line", thickness=2), color=self.default_color
        )


class ButtonPrefab(Button):
    def __init__(self, **kwargs):
        super().__init__(scale=Vec2(0.2, 0.08), **kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90


class FileButton(Button):
    def __init__(self, path, **kwargs):
        super().__init__(scale=(0.5, 0.05), color=color.black50, text_size=1.2, pressed_scale=1, **kwargs)

        self.path = path

        self.original_color = self.color
        self.highlight_color = color.black66
        self.pressed_color = color.black90
        self.selected = False

    def on_click(self):
        if not self.selected:
            for e in self.parent.children:
                e.selected = False

        self.selected = True

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

        if value:
            self.color = self.pressed_color

        else:
            self.color = self.original_color


class ItemButton(Button):
    def __init__(self, voxel_id, **kwargs):
        super().__init__(model="quad", **kwargs)

        from src.resource_loader import instance as resource_loader

        self.voxel_id = voxel_id
        self.scale = 0.05

        self.selector = Entity(parent=self, scale=1.25, model="quad", shader=resource_loader.selector_shader)

        side_texture_id = resource_loader.texture_types[self.voxel_id * 3 - 1]

        self.shader = resource_loader.voxel_display_shader
        self.set_shader_input("texture_array", resource_loader.texture_array)
        self.set_shader_input("texture_id", int(side_texture_id))

        self.selected = False

    def on_click(self):
        if not self.selected:
            for e in self.parent.children:
                e.selected = False

        self.selected = True

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

        if value:
            self.selector.enable()
            self.scale = 0.06

        else:
            self.selector.disable()
            self.scale = 0.05


class ThinSlider(Slider):
    def __init__(self, **kwargs):
        kwargs["height"] = Text.size
        super().__init__(**kwargs)

        self.bg.model = Quad(scale=(0.525, Text.size / 2), radius=Text.size / 4, segments=3)
        self.bg.origin = self.bg.origin
