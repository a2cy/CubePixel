# cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
cimport numpy as np
import numpy as np


np.import_array()

cdef int[18] face_0 = [0, 0, 0,
                       0, 1, 0,
                       0, 1, 1,
                       0, 1, 1,
                       0, 0, 1,
                       0, 0, 0,]

cdef int[18] face_1 = [0, 0, 0,
                       0, 0, 1,
                       1, 0, 1,
                       1, 0, 1,
                       1, 0, 0,
                       0, 0, 0,]

cdef int[18] face_2 = [0, 0, 0,
                       1, 0, 0,
                       1, 1, 0,
                       1, 1, 0,
                       0, 1, 0,
                       0, 0, 0,]

cdef int[18] face_3 = [1, 0, 0,
                       1, 0, 1,
                       1, 1, 1,
                       1, 1, 1,
                       1, 1, 0,
                       1, 0, 0,]

cdef int[18] face_4 = [0, 1, 0,
                       1, 1, 0,
                       1, 1, 1,
                       1, 1, 1,
                       0, 1, 1,
                       0, 1, 0,]

cdef int[18] face_5 = [0, 0, 1,
                       0, 1, 1,
                       1, 1, 1,
                       1, 1, 1,
                       1, 0, 1,
                       0, 0, 1,]

cdef int[18] neighbor_offsets = [-1,0,0,  0,-1,0,  0,0,-1,  1,0,0,  0,1,0,  0,0,1]


cdef void copy_face(int index, int x, int y, int z, int texture_id, int normal_id, const int *face, unsigned int *vertex_data) noexcept nogil:
    cdef int i, x_position, y_position, z_position

    for i in range(6):
        x_position = face[i * 3 + 0] + x
        y_position = face[i * 3 + 1] + y
        z_position = face[i * 3 + 2] + z

        # pack vertex data into uint32
        vertex_data[index * 6 + i] = x_position | y_position << 6 | z_position << 12 | normal_id << 18 | texture_id << 21


cdef int check_occlusion(int chunk_size, int index, int x, int y, int z, int *occlusion_types, unsigned char *occlusion_state, unsigned char *voxel_data, long long *neighbors) noexcept nogil:
    cdef int i, x_position, y_position, z_position, face_count = 0
    cdef unsigned char voxel_id = voxel_data[x * chunk_size * chunk_size + y * chunk_size + z]
    cdef unsigned char neighbor_id, result = 0
    cdef unsigned char *neighbor_chunk

    for i in range(6):
        x_position = neighbor_offsets[i * 3 + 0] + x
        y_position = neighbor_offsets[i * 3 + 1] + y
        z_position = neighbor_offsets[i * 3 + 2] + z

        if x_position < 0:
            neighbor_chunk = <unsigned char*>neighbors[0]
            x_position += chunk_size

        elif x_position >= chunk_size:
            neighbor_chunk = <unsigned char*>neighbors[3]
            x_position -= chunk_size

        elif y_position < 0:
            neighbor_chunk = <unsigned char*>neighbors[1]
            y_position += chunk_size

        elif y_position >= chunk_size:
            neighbor_chunk = <unsigned char*>neighbors[4]
            y_position -= chunk_size

        elif z_position < 0:
            neighbor_chunk = <unsigned char*>neighbors[2]
            z_position += chunk_size

        elif z_position >= chunk_size:
            neighbor_chunk = <unsigned char*>neighbors[5]
            z_position -= chunk_size

        else:
            neighbor_chunk = voxel_data

        if neighbor_chunk:
            neighbor_id = neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + z_position]

        else:
            continue

        if neighbor_id == voxel_id:
            continue

        if not neighbor_id or not occlusion_types[neighbor_id - 1]:
            result |= 1 << i
            face_count += 1

    occlusion_state[index] = result
    return face_count


def generate_mesh(int chunk_size, int [:] texture_types, int [:] occlusion_types, unsigned char [:]voxel_data, long long [:]neighbors):
    cdef int i, x, y, z, side, up, down, occlusion
    cdef int face_count = 0
    cdef np.ndarray[unsigned char, ndim=1] _occlusion_state = np.zeros(chunk_size**3, dtype=np.ubyte)
    cdef unsigned char *occlusion_state = &_occlusion_state[0]

    with nogil:
        for i in range(chunk_size**3):
            if not voxel_data[i]:
                continue

            x = i / (chunk_size * chunk_size)
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            face_count += check_occlusion(chunk_size, i, x, y, z, &occlusion_types[0], occlusion_state, &voxel_data[0], &neighbors[0])

    cdef np.ndarray[unsigned int, ndim=1] vertex_data = np.zeros(face_count * 6, dtype=np.uintc)
    cdef int index = 0

    with nogil:
        for i in range(chunk_size**3):
            if not occlusion_state[i]:
                continue

            x = i / (chunk_size * chunk_size)
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            side = texture_types[voxel_data[i] * 3 - 1]
            up   = texture_types[voxel_data[i] * 3 - 3]
            down = texture_types[voxel_data[i] * 3 - 2]

            occlusion = occlusion_state[i]

            if occlusion & 32:
                copy_face(index, x, y, z, side, 5, face_5, &vertex_data[0])
                index += 1

            if occlusion & 16:
                copy_face(index, x, y, z, up, 4, face_4, &vertex_data[0])
                index += 1

            if occlusion & 8:
                copy_face(index, x, y, z, side, 3, face_3, &vertex_data[0])
                index += 1

            if occlusion & 4:
                copy_face(index, x, y, z, side, 2, face_2, &vertex_data[0])
                index += 1

            if occlusion & 2:
                copy_face(index, x, y, z, down, 1, face_1, &vertex_data[0])
                index += 1

            if occlusion & 1:
                copy_face(index, x, y, z, side, 0, face_0, &vertex_data[0])
                index += 1

    return vertex_data
