# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# distutils: language=c++


cimport numpy as np
import numpy as np

from libcpp.vector cimport vector
from libcpp cimport bool


np.import_array()


cdef extern from "cpp_functions.cpp":

    cdef struct GameEntity:
        unsigned int shape
        float* vertices
        float* uvs
        bool transparent
        bool solid


    cdef cppclass WorldGeneratorCpp:

        WorldGeneratorCpp() except +

        vector[GameEntity] entity_data

        bool check_occlusion(unsigned short chunk_size, int* position, unsigned short* entities, long* neighbors)

        void combine_mesh(unsigned short chunk_size, unsigned short* entities, int* position, float* vertices, float* uvs, int* indices)


cdef class PyGameEntity:
    cdef public unsigned int shape
    cdef public float [:] vertices
    cdef public float [:] uvs
    cdef public bool transparent
    cdef public bool solid


cdef class WorldGenerator:

    cdef WorldGeneratorCpp world_generator


    def __init__(self, PyGameEntity [:] py_entity_data):
        cdef int i

        for i in range(py_entity_data.shape[0]):
            self.world_generator.entity_data.push_back(GameEntity(py_entity_data[i].shape, &py_entity_data[i].vertices[0], &py_entity_data[i].uvs[0], <bool>py_entity_data[i].transparent, <bool>py_entity_data[i].solid))


    def generate_chunkentities(self, unsigned short chunk_size, noise2, noise3, unsigned short amp, unsigned short freq2, unsigned short freq3, int [:] position):
        cdef int i, threshold, max_y
        cdef float x, y, z

        cdef np.ndarray[unsigned short, ndim=1] entities = np.zeros(chunk_size**3, dtype=np.ushort)

        for i in range(chunk_size**3):
            x = i // chunk_size // chunk_size - (chunk_size - 1) / 2 + position[0]
            y = i // chunk_size % chunk_size - (chunk_size - 1) / 2 + position[1]
            z = i % chunk_size % chunk_size - (chunk_size - 1) / 2 + position[2]

            if not freq3 == 0:
                threshold = noise3(x / freq3, y / freq3, z / freq3)

                if threshold < 0:
                    entities[i] = 0
                    continue

            max_y = noise2(x / freq2, z / freq2) * amp + amp / 2

            if y == max_y:
                entities[i] = 1

            elif y < max_y:
               entities[i] = 2

            else:
               entities[i] = 0

        return entities


    cpdef combine_mesh(self, unsigned short chunk_size , int [:] position, unsigned short [:] entities, long [:] neighbors):
        cdef int i, shape, vertex_count = 0
        cdef int entity_position[3]
        cdef np.ndarray[int, ndim=1] indices = np.zeros((chunk_size**3), dtype=np.intc)

        for i in range(chunk_size**3):
            shape = self.world_generator.entity_data[entities[i]].shape

            if shape == 0:
                indices[i] = -1
                continue

            entity_position[0] = i / chunk_size / chunk_size
            entity_position[1] = i / chunk_size % chunk_size
            entity_position[2] = i % chunk_size % chunk_size

            if self.world_generator.check_occlusion(chunk_size, entity_position, &entities[0], &neighbors[0]):
                indices[i] = -1
                continue

            indices[i] = vertex_count

            vertex_count += shape

        cdef np.ndarray[float, ndim=1] vertices = np.zeros((vertex_count*3), dtype=np.single)
        cdef np.ndarray[float, ndim=1] uvs = np.zeros((vertex_count*3), dtype=np.single)

        if not vertex_count == 0:
            self.world_generator.combine_mesh(chunk_size, &entities[0], &position[0], &vertices[0], &uvs[0], &indices[0])

        return [vertices, uvs]
