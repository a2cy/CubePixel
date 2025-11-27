from ursina import Button, Entity, InputField, Func, Quad, Slider, Text, Vec2, color

from .resource_loader import resource_loader


class MenuButton(Entity):
    def __init__(self, text: str, **kwargs) -> None:
        on_click = kwargs.pop("on_click") if "on_click" in kwargs else None
        super().__init__(**kwargs)

        self.default_color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90

        self._background = Entity(
            parent=self,
            model="quad",
            collider="box",
            scale=Vec2(0.3, 0.08),
            z=0.5,
            color=self.default_color,
            on_click=on_click,
            shader=resource_loader.outline_shader,
        )
        self._background.set_shader_inputs(u_outline_color=color.light_gray, u_thickness=0.04)
        self._background.on_mouse_enter = Func(setattr, self._background, "color", self.highlight_color)
        self._background.on_mouse_exit = Func(setattr, self._background, "color", self.default_color)

        self._text_entity = Text(parent=self, text=text, origin=Vec2(0, 0), add_to_scene_entities=False)

    def input(self, key: str) -> None:
        if key == "left mouse down" and self._background.hovered:
            self._background.color = self.pressed_color

        if key == "left mouse up":
            if self._background.hovered:
                self._background.color = self.highlight_color

            else:
                self._background.color = self.default_color


class MenuContent(Entity):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(position=Vec2(0.25, 0), **kwargs)

        self._background = Entity(
            parent=self,
            model="quad",
            color=color.black50,
            shader=resource_loader.outline_shader,
            scale=Vec2(1.2, 1.02),
            z=1,
        )
        self._background.set_shader_inputs(u_outline_color=color.black90, u_thickness=0.04)

        self._label = Text(parent=self, text=text, scale=1.5, position=Vec2(0, 0.42), origin=Vec2(0, 0))


class InputFieldPrefab(InputField):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.text_field.cursor.origin_y = -0.4


class ButtonPrefab(Button):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            scale=Vec2(0.2, 0.08),
            color=color.black50,
            highlight_color=color.black66,
            pressed_color=color.black90,
            **kwargs,
        )


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

        self.selector = Entity(parent=self, scale=1.25, color=color.clear, model="quad", shader=resource_loader.outline_shader)
        self.selector.set_shader_inputs(u_outline_color=color.black50, u_thickness=0.04)

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
        self.button_count = 0
        self.on_scroll = None
        self._scroll = 0

        self._bg = Entity(parent=self, model=Quad(scale=(0.01, 0.6), radius=0.005, segments=3), z=0.5, color=color.black66)
        self._scroll_indicator = Entity(parent=self, model="quad", texture="mouse-scroll", y=0.3, color=color.smoke, scale=0.04)

    def update_indicator(self) -> None:
        scroll_percent = self._scroll / (self.button_count - self.max_buttons) if self.button_count > self.max_buttons else 0
        self._scroll_indicator.y = 0.29 - scroll_percent * 0.58

        if callable(self.on_scroll):
            self.on_scroll(self._scroll)

    def reset(self) -> None:
        self._scroll = 0
        self.update_indicator()

    def input(self, key: str) -> None:
        if key == "scroll down" and self._scroll + self.max_buttons < self.button_count:
            self._scroll += 1
            self.update_indicator()

        if key == "scroll up" and self._scroll > 0:
            self._scroll -= 1
            self.update_indicator()
