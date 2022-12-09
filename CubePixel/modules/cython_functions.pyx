import numpy as np
cimport numpy as cnp
cimport cython


@cython.boundscheck(False)
cpdef generate_chunkentities(int chunk_with, noise, int amp, int freq, tuple position, dict entity_index):
    cdef cnp.ndarray[cnp.float32_t, ndim=2] entities
    entities = np.zeros((chunk_with**3, 4), dtype=np.float32)

    cdef int i, x, y, z, max_y
    for i in range(len(entities)):
        x = int(i // chunk_with // chunk_with - (chunk_with - 1) / 2)
        y = int(i // chunk_with % chunk_with - (chunk_with - 1) / 2)
        z = int(i % chunk_with % chunk_with - (chunk_with - 1) / 2)

        max_y = int(noise((x + position[0]) / freq,
                    (z + position[2]) / freq) * amp + amp / 2)
            
        if y + position[1] == max_y:
            entities[i] = np.array([x, y, z, entity_index["grass"]], dtype=np.int32)
        elif y + position[1] < max_y:
            entities[i] = np.array([x, y, z, entity_index["stone"]], dtype=np.int32)
        else:
            entities[i] = np.array([x, y, z, entity_index["air"]], dtype=np.int32)

    return entities


@cython.boundscheck(False)
cpdef combine_mesh(list entity_data, int chunk_with, cnp.ndarray[cnp.float32_t, ndim=2] entities):
    cdef int vertex_count = 0
    cdef int i
    for i in range(len(entity_data)):
        if entity_data[i] == None:
            continue
        
        vertex_count += len(entities[entities[:, 3]==i])*len(entity_data[i][0])

    cdef cnp.ndarray[cnp.float32_t, ndim=2] vertices
    cdef cnp.ndarray[cnp.float32_t, ndim=2] uvs
    cdef cnp.ndarray[cnp.float32_t, ndim=2] normals

    vertices = np.zeros((vertex_count, 3), dtype=np.float32)
    uvs = np.zeros((vertex_count, 3), dtype=np.float32)
    normals = np.zeros((vertex_count, 3), dtype=np.float32)

    cdef int slice_index = 0
    cdef int new_slice_index, x, y, z
    cdef cnp.ndarray[cnp.float32_t, ndim=1] entity_position, entity
    cdef list model

    for i in range(len(entities)):
        entity = entities[i]
        entity_position = np.array([entity[0], entity[1], entity[2]], dtype=np.float32)
        model = entity_data[int(entity[3])]
        if model == None:
            continue

        new_slice_index = slice_index + len(model[0])

        vertices[slice_index:new_slice_index] = model[0]+entity_position
        uvs[slice_index:new_slice_index] = model[1]
        normals[slice_index:new_slice_index] = model[2]

        slice_index = new_slice_index

    cdef list result = [vertices, uvs, normals]

    return result
