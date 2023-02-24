# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True, binding=False


import numpy as np
cimport numpy as cnp


cdef class GameEntity:
    cdef public float [:, :] vertices
    cdef public float [:, :] uvs
    cdef public float [:, :] normals
    cdef public char transparent
    cdef public char solid


cpdef generate_chunkentities(int chunk_with, noise, int amp, int freq, float [:] position):
    cdef int i, x, y, z, max_y

    cdef cnp.ndarray[int, ndim=3] entities = np.zeros((chunk_with, chunk_with, chunk_with), dtype=np.int32)

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


cdef void transpose_vertices(float [:, :] vertices, int [:] position, float [:, :] result) nogil:
    cdef int i

    for i in range(vertices.shape[0]):
        result[i, 0] = vertices[i, 0] + position[0]
        result[i, 1] = vertices[i, 1] + position[1]
        result[i, 2] = vertices[i, 2] + position[2]


cpdef combine_mesh(GameEntity [:] entity_data, int [:, :, :] entities, int [:] position):
    cdef int i, j, x, y, z, count, new_slice_index, vertex_count = 0, slice_index = 0

    cdef int chunk_with = entities.shape[0]

    cdef int _entity_position[3]
    cdef int [:] entity_position = _entity_position
    cdef GameEntity entity

    for i in range(entity_data.shape[0]):
        if entity_data[i].vertices.shape[0] == 0:
            continue

        count = 0
        for j in range(chunk_with**3):
            x = j // chunk_with // chunk_with
            y = j // chunk_with % chunk_with
            z = j % chunk_with % chunk_with

            if entities[x, y, z] == i:
                count += entity_data[i].vertices.shape[0]

        vertex_count += count


    cdef cnp.ndarray[float, ndim=2] vertices = np.zeros((vertex_count, 3), dtype=np.float32)
    cdef cnp.ndarray[float, ndim=2] uvs = np.zeros((vertex_count, 3), dtype=np.float32)
    cdef cnp.ndarray[float, ndim=2] normals = np.zeros((vertex_count, 3), dtype=np.float32)

    cdef float [:, :] vertices_view = vertices
    cdef float [:, :] uvs_view = uvs
    cdef float [:, :] normals_view = normals

    for i in range(chunk_with**3):
        x = i // chunk_with // chunk_with
        y = i // chunk_with % chunk_with
        z = i % chunk_with % chunk_with

        entity_position[0] = x - (chunk_with - 1) / 2 + position[0]
        entity_position[1] = y - (chunk_with - 1) / 2 + position[1]
        entity_position[2] = z - (chunk_with - 1) / 2 + position[2]

        entity = entity_data[entities[x, y, z]]

        if entity.vertices.shape[0] == 0:
            continue

        new_slice_index = slice_index + entity.vertices.shape[0]

        transpose_vertices(entity.vertices, entity_position, vertices_view[slice_index:new_slice_index])
        uvs_view[slice_index:new_slice_index] = entity.uvs
        normals_view[slice_index:new_slice_index] = entity.normals

        slice_index = new_slice_index

    return [vertices, uvs, normals]
