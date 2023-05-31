import numpy as np

from panda3d.core import NodePath, Geom, GeomNode, GeomVertexFormat, GeomVertexArrayFormat, GeomVertexData, GeomTriangles, GeomEnums


class ChunkMesh(NodePath):

    v_array = GeomVertexArrayFormat()
    v_array.addColumn("vertex", 3, Geom.NTFloat32, Geom.CPoint)

    t_array = GeomVertexArrayFormat()
    t_array.addColumn("texcoord", 3, Geom.NTFloat32, Geom.CTexcoord)

    vertex_format = GeomVertexFormat()
    vertex_format.addArray(v_array)
    vertex_format.addArray(t_array)
    vertex_format = GeomVertexFormat.registerFormat(vertex_format)

    def __init__(self, **kwargs):
        super().__init__("chunk_mesh")
        self.name = "chunk_mesh"

        self.geom_node = GeomNode("chunk_mesh")
        self.attachNewNode(self.geom_node)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def add_chunk(self, vertices=None, uvs=None):
        if vertices is None:
            return

        v_data = GeomVertexData("chunk", self.vertex_format, Geom.UH_static)
        v_data.unclean_set_num_rows(len(vertices)//3)

        memview = memoryview(v_data.modify_array(0)).cast("B").cast("f")
        memview[:] = vertices

        if uvs is not None:
            memview = memoryview(v_data.modify_array(1)).cast("B").cast("f")
            memview[:] = uvs

        prim = GeomTriangles(Geom.UH_static)
        prim.set_index_type(GeomEnums.NT_uint32)

        p_array = prim.modify_vertices()
        p_array.unclean_set_num_rows(len(vertices)//3)

        memview = memoryview(p_array).cast("B").cast("I")
        memview[:] = np.arange(len(vertices)//3, dtype=np.uintc)
        
        geom = Geom(v_data)
        geom.addPrimitive(prim)
        self.geom_node.addGeom(geom)


    def remove_chunk(self, index):
        self.geom_node.removeGeom(index)
