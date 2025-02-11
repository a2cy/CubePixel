from panda3d.core import NodePath, BoundingSphere, TransparencyAttrib, Vec3
from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexArrayFormat, GeomVertexData, GeomTriangles


class VoxelChunk(NodePath):

    v_array = GeomVertexArrayFormat()
    v_array.add_column("vertex", 3, Geom.NT_float32, Geom.C_point)

    t_array = GeomVertexArrayFormat()
    t_array.add_column("vertex_data", 2, Geom.NT_uint16, Geom.C_other)

    vertex_format = GeomVertexFormat()
    vertex_format.add_array(v_array)
    vertex_format.add_array(t_array)
    vertex_format = GeomVertexFormat.register_format(vertex_format)

    def __init__(self, chunk_size, shader=None, **kwargs):
        super().__init__("voxel_chunk", **kwargs)

        if shader:
            self.set_shader(shader)
            self.set_transparency(TransparencyAttrib.M_dual)

        self.geom_node = GeomNode("voxel_chunk")
        self.attach_new_node(self.geom_node)

        v_data = GeomVertexData("voxel_chunk", self.vertex_format, Geom.UH_static)
        prim = GeomTriangles(Geom.UH_static)

        geom = Geom(v_data)
        geom.add_primitive(prim)
        geom.set_bounds(BoundingSphere(Vec3(chunk_size/2), chunk_size))
        self.final = True

        self.geom_node.add_geom(geom)


    def update(self, vertices=None, vertex_data=None):
        if vertices is None:
            return

        geom = self.geom_node.modify_geom(0)

        v_data = geom.modify_vertex_data()
        prim = geom.modify_primitive(0)

        v_data.unclean_set_num_rows(len(vertices)//3)

        memview = memoryview(v_data.modify_array(0)).cast("B").cast("f")
        memview[:] = vertices

        if not vertex_data is None:
            memview = memoryview(v_data.modify_array(1)).cast("B").cast("H")
            memview[:] = vertex_data

        prim.clear_vertices()
        prim.add_next_vertices(len(vertices)//3)
