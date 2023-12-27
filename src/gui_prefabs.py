from ursina import Entity, Text, Mesh, Vec2, color


class MenuButton(Entity):

    def __init__(self, text="", **kwargs):
        super().__init__()

        self.disabled = False
        self.selected = False
        self.model = "quad"
        self.collider = "box"
        self.scale=Vec2(.3, .08)
        self.color = color.clear

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.default_color = color.black
        self.highlight_color = color.azure
        self.selected_color = color.smoke
        self.pressed_color = color.orange
        self.disabled_color = color.gray

        self.background = Entity(parent=self, model=Mesh(vertices=[(-.4,-.4,0), (.4,-.4,0)], mode="line", thickness=2), color=self.default_color)

        self.text_entity = Text(parent=self, text=text, scale=(self.scale*50).yx, origin=Vec2(0, 0), color=self.default_color, add_to_scene_entities=False)


    def input(self, key):
        if self.disabled or not self.model:
            return

        if key == 'left mouse down':
            if self.hovered:
                self.background.color = self.pressed_color
                self.text_entity.color = self.pressed_color

        if key == 'left mouse up':
            if self.hovered:
                self.background.color = self.highlight_color
                self.text_entity.color = self.highlight_color

            else:
                self.background.color = self.default_color if not self.selected else self.selected_color
                self.text_entity.color = self.default_color if not self.selected else self.selected_color


    def on_mouse_enter(self):
        self.background.color = self.highlight_color
        self.text_entity.color = self.highlight_color


    def on_mouse_exit(self):
        self.background.color = self.default_color if not self.selected else self.selected_color
        self.text_entity.color = self.default_color if not self.selected else self.selected_color


if __name__ == "__main__":
    from ursina import *

    app = Ursina(borderless=False)

    text_default = Text("Default", color=color.black, position=Vec2(-.8, .4))
    text_highlighted = Text("Highlighted", color=color.azure, position=Vec2(-.8, .3))
    text_selected = Text("Selected", color=color.smoke, position=Vec2(-.8, .2))
    text_pressed = Text("Pressed", color=color.orange, position=Vec2(-.8, .1))
    text_disabled = Text("Disabled", color=color.gray, position=Vec2(-.8, .0))

    app.run()