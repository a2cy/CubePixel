from panda3d.core import NodePath, Geom, GeomNode, GeomVertexFormat, GeomVertexArrayFormat, GeomVertexData, GeomTriangles, TransparencyAttrib


class VoxelChunk(NodePath):

    v_array = GeomVertexArrayFormat()
    v_array.add_column("vertex", 3, Geom.NT_float32, Geom.C_point)

    t_array = GeomVertexArrayFormat()
    t_array.add_column("texcoord", 3, Geom.NT_float32, Geom.C_texcoord)

    vertex_format = GeomVertexFormat()
    vertex_format.add_array(v_array)
    vertex_format.add_array(t_array)
    vertex_format = GeomVertexFormat.register_format(vertex_format)

    def __init__(self, **kwargs):
        super().__init__("voxel_chunk", **kwargs)

        self.set_transparency(TransparencyAttrib.M_dual)

        self.geom_node = GeomNode("voxel_chunk")
        self.attach_new_node(self.geom_node)

        v_data = GeomVertexData("voxel_chunk", self.vertex_format, Geom.UH_static)
        prim = GeomTriangles(Geom.UH_static)
        prim.set_index_type(Geom.NT_uint32)

        geom = Geom(v_data)
        geom.add_primitive(prim)

        self.geom_node.add_geom(geom)


    def update(self, vertices=None, uvs=None):
        if vertices is None or len(vertices) == 0:
            return

        geom = self.geom_node.modify_geom(0)

        v_data = geom.modify_vertex_data()
        prim = geom.modify_primitive(0)

        v_data.unclean_set_num_rows(len(vertices)//3)

        memview = memoryview(v_data.modify_array(0)).cast("B").cast("f")
        memview[:] = vertices

        if not uvs is None or not len(uvs) == 0:
            memview = memoryview(v_data.modify_array(1)).cast("B").cast("f")
            memview[:] = uvs

        prim.clear_vertices()
        prim.add_next_vertices(len(vertices)//3)
