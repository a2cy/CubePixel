# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
# distutils: language=c++


import numpy as np
cimport numpy as np

from libcpp.vector cimport vector
from cpython.ref cimport PyObject
from libcpp cimport bool


np.import_array()


cdef extern from "cpp_functions.cpp":

    cdef struct GameEntity:
        int shape
        float* vertices
        float* uvs
        bool transparent
        bool solid
    

    cdef cppclass WordGeneratorCpp:

        WordGeneratorCpp() except +

        vector[GameEntity] entity_data

        void combine_mesh(int* entities, int chunk_with, int* position, float* vertices, float* uvs, int* indices)


cdef class WordGenerator:
    
    cdef WordGeneratorCpp world_generator


    def __cinit__(self, np.ndarray[object, ndim=1] _entity_data):
        self.world_generator = WordGeneratorCpp()

        cdef int i
        cdef vector[GameEntity] entity_data
        cdef GameEntity game_entity

        cdef np.ndarray[float, ndim=2] vertices
        cdef np.ndarray[float, ndim=2] uvs

        for i in range(_entity_data.shape[0]):
            vertices = _entity_data[i].vertices
            uvs = _entity_data[i].uvs

            if _entity_data[i].vertices is None:
                entity_data.push_back(GameEntity(0, &vertices[0, 0], &uvs[0, 0], <bool>_entity_data[i].transparent, <bool>_entity_data[i].solid))
                continue

            entity_data.push_back(GameEntity(<int>vertices.shape[0], &vertices[0, 0], &uvs[0, 0], <bool>_entity_data[i].transparent, <bool>_entity_data[i].solid))

        self.world_generator.entity_data = entity_data


    cpdef generate_chunkentities(self, int chunk_with, noise, int amp, int freq, float [:] position):
        cdef int i, x, y, z, max_y
        cdef np.ndarray[int, ndim=3] entities = np.zeros((chunk_with, chunk_with, chunk_with), dtype=np.intc)
        cdef int [:, :, :] entities_view = entities

        for i in range(chunk_with**3):
            x = i // chunk_with // chunk_with
            y = i // chunk_with % chunk_with
            z = i % chunk_with % chunk_with

            max_y = noise(((x - (chunk_with - 1) / 2) + position[0]) / freq,
                    ((z - (chunk_with - 1) / 2) + position[2]) / freq) * amp + amp / 2

            if (y - (chunk_with - 1) / 2) + position[1] == max_y:
                entities_view[x, y, z] = 1

            elif (y - (chunk_with - 1) / 2) + position[1] < max_y:
               entities_view[x, y, z] = 2

            else:
               entities_view[x, y, z] = 0

        return entities


    cpdef combine_mesh(self, np.ndarray[int, ndim=3] entities, np.ndarray[int, ndim=1] position):
        cdef int i, x, y, z, vertex_count = 0
        cdef int chunk_with = entities.shape[0]
        cdef np.ndarray[int, ndim=1] indices = np.zeros((chunk_with**3), dtype=np.intc)

        for i in range(chunk_with**3):
            x = i / chunk_with / chunk_with
            y = i / chunk_with % chunk_with
            z = i % chunk_with % chunk_with

            if self.world_generator.entity_data[entities[x, y, z]].shape == 0:
                continue

            indices[i] = vertex_count

            vertex_count += self.world_generator.entity_data[entities[x, y, z]].shape

        cdef np.ndarray[float, ndim=2] vertices = np.zeros((vertex_count, 3), dtype=np.single)
        cdef np.ndarray[float, ndim=2] uvs = np.zeros((vertex_count, 3), dtype=np.single)

        self.world_generator.combine_mesh(&entities[0, 0, 0], <int>entities.shape[0], &position[0], &vertices[0, 0], &uvs[0, 0], &indices[0])

        return [vertices, uvs]
