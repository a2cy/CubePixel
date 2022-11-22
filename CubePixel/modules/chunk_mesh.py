import numpy as np

from panda3d.core import NodePath, Geom, GeomNode, GeomVertexFormat, GeomVertexArrayFormat, GeomVertexData, GeomTriangles, GeomEnums

class ChunkMesh(NodePath):

    v_array = GeomVertexArrayFormat()
    v_array.addColumn("vertex", 3, Geom.NTFloat32, Geom.CPoint)

    t_array = GeomVertexArrayFormat()
    t_array.addColumn("texcoord", 2, Geom.NTFloat32, Geom.CTexcoord)

    n_array = GeomVertexArrayFormat()
    n_array.addColumn("normal", 3, Geom.NTFloat32, Geom.CPoint)

    vertex_format = GeomVertexFormat()
    vertex_format.addArray(v_array)
    vertex_format.addArray(t_array)
    vertex_format.addArray(n_array)
    vertex_format = GeomVertexFormat.registerFormat(vertex_format)

    def __init__(self, vertices=None, uvs=None, normals=None):
        super().__init__('chunk_mesh')
        self.name = 'chunk_mesh'
        self.vertices = vertices
        self.uvs = uvs
        self.normals = normals

        if self.vertices is not None:
            self.generate()


    def generate(self):
        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()

        if not hasattr(self, 'geomNode'):
            self.geomNode = GeomNode('mesh')
            self.attachNewNode(self.geomNode)

        v_data = GeomVertexData('name', self.vertex_format, Geom.UH_static)
        v_data.set_num_rows(len(self.vertices)//3)

        memview = memoryview(v_data.modify_array(0)).cast("B").cast("f")
        memview[:] = self.vertices

        if self.uvs is not None:
            memview = memoryview(v_data.modify_array(1)).cast("B").cast("f")
            memview[:] = self.uvs

        if self.normals is not None:
            memview = memoryview(v_data.modify_array(2)).cast("B").cast("f")
            memview[:] = self.normals

        prim = GeomTriangles(Geom.UH_static)
        prim.set_index_type(GeomEnums.NT_uint32)

        p_array = prim.modify_vertices()
        p_array.set_num_rows(len(self.vertices)//3)

        memview = memoryview(p_array).cast("B").cast("I")
        memview[:] = np.arange(len(self.vertices)//3, dtype=np.uint32)

        geom = Geom(v_data)
        geom.addPrimitive(prim)
        self.geomNode.addGeom(geom)
