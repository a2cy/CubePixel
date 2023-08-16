from ursina import Entity
from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexArrayFormat, GeomVertexData, GeomTriangles, BoundingSphere


class Chunk(Entity):

    v_array = GeomVertexArrayFormat()
    v_array.add_column("vertex", 3, Geom.NT_float32, Geom.C_point)

    t_array = GeomVertexArrayFormat()
    t_array.add_column("texcoord", 3, Geom.NT_float32, Geom.C_texcoord)

    vertex_format = GeomVertexFormat()
    vertex_format.add_array(v_array)
    vertex_format.add_array(t_array)
    vertex_format = GeomVertexFormat.register_format(vertex_format)

    def __init__(self, chunk_size, position, vertices=None, uvs=None, **kwargs):
        super().__init__("chunk")
        self.name = "chunk"

        self.vertices = vertices
        self.uvs = uvs

        self.geom_node = GeomNode("chunk")
        self.attach_new_node(self.geom_node)

        v_data = GeomVertexData("chunk", self.vertex_format, Geom.UH_static)
        prim = GeomTriangles(Geom.UH_static)
        prim.set_index_type(Geom.NT_uint32)

        geom = Geom(v_data)
        geom.add_primitive(prim)
        geom.set_bounds(BoundingSphere(position, chunk_size * 3 / 2 * 1.5))
        self.final = True

        self.geom_node.add_geom(geom)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update_mesh(self):
        if self.vertices is None or len(self.vertices) == 0:
            return

        geom = self.geom_node.modify_geom(0)

        v_data = geom.modify_vertex_data()
        prim = geom.modify_primitive(0)

        v_data.unclean_set_num_rows(len(self.vertices)//3)

        memview = memoryview(v_data.modify_array(0)).cast("B").cast("f")
        memview[:] = self.vertices

        if not self.uvs is None or not len(self.uvs) == 0:
            memview = memoryview(v_data.modify_array(1)).cast("B").cast("f")
            memview[:] = self.uvs

        prim.clear_vertices()
        prim.add_next_vertices(len(self.vertices)//3)
