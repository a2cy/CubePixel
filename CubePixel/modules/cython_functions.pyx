# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True, binding=False


import numpy as np
cimport numpy as cnp


def generate_chunkentities(int chunk_with, noise, int amp, int freq, tuple position, dict entity_index):
    cdef int i, x, y, z, max_y
    cdef cnp.ndarray[float, ndim=2] entities

    entities = np.zeros((chunk_with**3, 4), dtype=np.float32)

    for i in range(entities.shape[0]):
        x = i // chunk_with // chunk_with - (chunk_with - 1) / 2
        y = i // chunk_with % chunk_with - (chunk_with - 1) / 2
        z = i % chunk_with % chunk_with - (chunk_with - 1) / 2

        max_y = noise((x + position[0]) / freq,
                    (z + position[2]) / freq) * amp + amp / 2

        if y + position[1] == max_y:
            entities[i] = np.array([x, y, z, entity_index["grass"]], dtype=np.int32)
        elif y + position[1] < max_y:
            entities[i] = np.array([x, y, z, entity_index["stone"]], dtype=np.int32)
        else:
            entities[i] = np.array([x, y, z, entity_index["air"]], dtype=np.int32)

    return entities


cdef float [:, :] transpose_vertices(float [:, :] vertices, float [:] position) nogil:
    for i in range(vertices.shape[0]):
        vertices[i][0] += position[0]
        vertices[i][1] += position[1]
        vertices[i][2] += position[2]

    return vertices


def combine_mesh(list entity_data, float[:, :] entities):
    cdef int i, count, new_slice_index
    cdef int vertex_count = 0
    cdef int slice_index = 0

    cdef float [:] entity, entity_position
    cdef float [:, :, :] model

    for i in range(len(entity_data)):
        if entity_data[i] is None:
            continue

        count = 0
        for j in range(entities.shape[0]):
            if entities[j][3] == i:
                count += entity_data[i][0].shape[0]

        vertex_count += count

    cdef cnp.ndarray[float, ndim=2] vertices = np.zeros((vertex_count, 3), dtype=np.float32)
    cdef cnp.ndarray[float, ndim=2] uvs = np.zeros((vertex_count, 3), dtype=np.float32)
    cdef cnp.ndarray[float, ndim=2] normals = np.zeros((vertex_count, 3), dtype=np.float32)

    cdef float [:, :] vertices_view = vertices
    cdef float [:, :] uvs_view = uvs
    cdef float [:, :] normals_view = normals

    for i in range(entities.shape[0]):
        entity = entities[i]
        entity_position = entity[0 : 3]
        model = entity_data[<int>entity[3]]
        if model is None:
            continue

        new_slice_index = slice_index + model[0].shape[0]

        vertices_view[slice_index:new_slice_index] = transpose_vertices(model[0].copy(), entity_position)
        uvs_view[slice_index:new_slice_index] = model[1]
        normals_view[slice_index:new_slice_index] = model[2]

        slice_index = new_slice_index

    return [vertices, uvs, normals]
