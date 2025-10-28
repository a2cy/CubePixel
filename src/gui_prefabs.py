from ursina import Entity, Button, Slider, Text, Mesh, Vec2, color, Quad, window
from ursina import InputField as uInputField


class MenuButton(Entity):
    def __init__(self, text: str, default_color=color.black, **kwargs) -> None:
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

    def input(self, key: str) -> None:
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

    def on_mouse_enter(self) -> None:
        self.background.color = self.highlight_color
        self.text_entity.color = self.highlight_color

    def on_mouse_exit(self) -> None:
        self.background.color = self.default_color
        self.text_entity.color = self.default_color


class MenuContent(Entity):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(**kwargs)

        self._background_panel = Entity(
            parent=self, model="quad", color=color.black50, position=window.right + Vec2(-0.65, 0), scale=Vec2(1.2, 1), z=1
        )

        self._panel_overlay = Entity(
            parent=self,
            model=Mesh(vertices=[(0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0), (-0.5, -0.5, 0)], mode="line", thickness=2),
            color=color.black90,
            position=window.right + Vec2(-0.65, 0),
            scale=Vec2(1.2, 1),
            z=1,
        )

        self._label = Text(parent=self, text=text, scale=1.5, position=window.right + Vec2(-0.65, 0.42), origin=Vec2(0, 0))


class InputField(uInputField):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.text_field.cursor.origin_y = -0.4


class ButtonPrefab(Button):
    def __init__(self, **kwargs) -> None:
        super().__init__(scale=Vec2(0.2, 0.08), **kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90


class FileButton(Button):
    def __init__(self, path: str, **kwargs) -> None:
        super().__init__(scale=(0.5, 0.05), color=color.black50, text_size=1.2, pressed_scale=1, **kwargs)

        self.path = path

        self.original_color = self.color
        self.highlight_color = color.black66
        self.pressed_color = color.black90
        self.selected = False

    def on_click(self) -> None:
        if not self.selected:
            for e in self.parent.children:
                e.selected = False

        self.selected = True

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value

        if value:
            self.color = self.pressed_color

        else:
            self.color = self.original_color


class ItemButton(Button):
    def __init__(self, voxel_id: int, **kwargs) -> None:
        super().__init__(model="quad", **kwargs)

        from src.resource_loader import resource_loader

        self.voxel_id = voxel_id
        self.scale = 0.05

        self.selector = Entity(parent=self, scale=1.25, model="quad", shader=resource_loader.selector_shader)

        side_texture_id = resource_loader.texture_types[self.voxel_id * 3 - 1]

        self.shader = resource_loader.voxel_display_shader
        self.set_shader_input("texture_array", resource_loader.texture_array)
        self.set_shader_input("texture_id", int(side_texture_id))

        self.selected = False

    def on_click(self) -> None:
        if not self.selected:
            for e in self.parent.children:
                e.selected = False

        self.selected = True

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value

        if value:
            self.selector.enable()
            self.scale = 0.06

        else:
            self.selector.disable()
            self.scale = 0.05


class ThinSlider(Slider):
    def __init__(self, **kwargs) -> None:
        kwargs["height"] = Text.size
        super().__init__(**kwargs)

        self.bg.model = Quad(scale=(0.525, Text.size / 2), radius=Text.size / 4, segments=3)
        self.bg.origin = self.bg.origin


class Scrollbar(Entity):
    def __init__(self, max_buttons: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.max_buttons = max_buttons
        self.button_count = 1
        self.on_scroll = None
        self._scroll = 0

        self._bg = Entity(parent=self, model=Quad(scale=(0.01, 0.6), radius=0.005, segments=3), color=color.black66)
        self._scroll_indicator = Entity(parent=self, model="quad", texture="caret-circle-up-down", color=color.white, scale=0.04)
        self._up_indicator = Button(
            parent=self,
            model="quad",
            texture="caret-circle-up",
            color=color.white,
            scale=0.04,
            position=Vec2(0, 0.35),
            highlight_scale=1.2,
            on_click=self.scroll_up,
        )
        self._down_indicator = Button(
            parent=self,
            model="quad",
            texture="caret-circle-down",
            color=color.white,
            scale=0.04,
            position=Vec2(0, -0.35),
            highlight_scale=1.2,
            on_click=self.scroll_down,
        )

    def scroll_up(self) -> None:
        if self._scroll > 0:
            self._scroll -= 1
            self.update_indicator()

    def scroll_down(self) -> None:
        if self._scroll + self.max_buttons < self.button_count:
            self._scroll += 1
            self.update_indicator()

    def update_indicator(self) -> None:
        scroll_percent = self._scroll / (self.button_count - self.max_buttons) if self.button_count > self.max_buttons else 0
        self._scroll_indicator.y = 0.3 - scroll_percent * 0.6

        if callable(self.on_scroll):
            self.on_scroll(self._scroll)

    def reset(self) -> None:
        self._scroll = 0
        self.update_indicator()

    def input(self, key: str) -> None:
        if key == "scroll down":
            self.scroll_down()

        if key == "scroll up":
            self.scroll_up()
