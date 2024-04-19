from ursina import Entity, Text, Mesh, Vec2, color, window


class MenuButton(Entity):

    def __init__(self, text="", **kwargs):
        super().__init__()

        self.model = "quad"
        self.collider = "box"
        self.scale=Vec2(.3, .08)
        self.color = color.clear

        for key, value in kwargs.items():
            setattr(self, key, value)

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


class MenuPanel(Entity):

    def __init__(self, text="", **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.background = Entity(parent=self,
                                 model="quad",
                                 color=color.black66,
                                 position=window.right+Vec2(-.65, 0),
                                 scale=Vec2(1.2, 1),
                                 z=1)

        self.background_overlay = Entity(parent=self,
                                         model=Mesh(vertices=[(.5,-.5,0), (.5,.5,0), (-.5,.5,0), (-.5,-.5,0)], mode="line", thickness=2),
                                         color=color.black90,
                                         position=window.right+Vec2(-.65, 0),
                                         scale=Vec2(1.2, 1),
                                         z=1)

        self.seperator = Entity(parent=self,
                                model=Mesh(vertices=[(.5,.4,0), (-.5,.4,0)], mode="line", thickness=1.4),
                                color=color.black90,
                                position=window.right+Vec2(-.65, 0),
                                scale=Vec2(1.2, 1),
                                z=1)

        self.label = Text(parent=self,
                          text=text,
                          scale=1.4,
                          position=window.right+Vec2(-.65, .43),
                          origin=Vec2(0, 0))