from ursina import Entity, Text, Mesh, Vec2, color, window
from ursina import InputField as uInputField, Button as Button


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


class ButtonPrefab(Button):

    def __init__(self, **kwargs):
        super().__init__(scale = Vec2(.2, .08), **kwargs)

        self.color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90


class FileButton(Button):
    def __init__(self, path, **kwargs):
        super().__init__(scale=(.5,.05), pressed_scale=1, **kwargs)

        self.path = path

        self.color = color.black50
        self.highlight_color = color.black66
        self.pressed_color = color.black90

        self.text_entity.scale *= 1.2
        self.original_color = self.color
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
        if value == True:
            self.color = self.pressed_color
        else:
            self.color = self.original_color


class ItemButton(Button):

    def __init__(self, voxel_id, **kwargs):
        super().__init__(**kwargs)

        from src.resource_loader import instance as resource_loader
        from src.chunk_manager import instance as chunk_manager
        from src.voxel_chunk import VoxelChunk

        self.voxel_id = voxel_id
        self.color = color.white
        self.highlight_color = color.white
        self.pressed_color = color.white
        self.scale = .05

        self.selector = Entity(parent=self, scale=1.25, model="quad", shader=resource_loader.selector_shader)

        self.model = VoxelChunk(chunk_manager.chunk_size, shader=resource_loader.voxel_shader)
        self.model.set_shader_input("texture_array", resource_loader.texture_array)
        self.model.reparent_to(self)

        voxel_type = resource_loader.voxel_types[self.voxel_id - 1]

        import numpy as np

        vertices = np.array([0, 0, 0,
                             1, 0, 0,
                             1, 1, 0,
                             1, 1, 0,
                             0, 1, 0,
                             0, 0, 0,],
        dtype=np.single)

        vertex_data = np.array([voxel_type.side, 3,
                                voxel_type.side, 3,
                                voxel_type.side, 3,
                                voxel_type.side, 3,
                                voxel_type.side, 3,
                                voxel_type.side, 3,],
        dtype=np.ushort)

        self.model.update(vertices, vertex_data)

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
        if value == True:
            self.selector.enable()
        else:
            self.selector.disable()