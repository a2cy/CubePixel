# cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
from fast_noise_lite cimport *

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


cdef class WorldGenerator:
    cdef int [:] texture_types
    cdef int [:] occlusion_types
    cdef fnl_state noise2d
    cdef float amp2d
    cdef int y_offset

    def __init__(self, int [:] texture_types, int [:] occlusion_types):
        self.texture_types = texture_types
        self.occlusion_types = occlusion_types

        self.noise2d = fnlCreateState()
        self.noise2d.noise_type = FNL_NOISE_OPENSIMPLEX2
        self.noise2d.fractal_type = FNL_FRACTAL_FBM
        self.noise2d.frequency = 0.002
        self.noise2d.gain = 1
        self.noise2d.octaves = 4

        self.amp2d = 32
        self.y_offset = 12

    def generate_voxels(self, int chunk_size, int seed, int chunk_x, int chunk_y, int chunk_z):
        cdef int i, index, x, y, z, world_y, diff, height
        cdef np.ndarray[unsigned char, ndim=1] voxel_data = np.zeros(chunk_size**3, dtype=np.ubyte)
        self.noise2d.seed = seed

        for i in range(chunk_size**2):
            x = i // chunk_size
            z = i % chunk_size
            height = <int>(fnlGetNoise2D(&self.noise2d, x + chunk_x, z + chunk_z) * self.amp2d + self.y_offset)

            for y in range(chunk_size):
                index = x * chunk_size * chunk_size + y * chunk_size + z
                world_y = y + chunk_y
                diff = height - world_y

                if diff == 0 and world_y >= 0:
                    voxel_data[index] = 2 # grass

                elif diff < 5 and diff >= 0:
                    voxel_data[index] = 1 # dirt

                elif diff >= 5:
                    voxel_data[index] = 3 # stone

                if world_y <= 0 and diff < 0:
                    voxel_data[index] = 5 # water

        return voxel_data

    def generate_mesh(self, int chunk_size, unsigned char [:] voxel_data, long long [:] neighbors):
        cdef int i, x, y, z, side, up, down, occlusion
        cdef int face_count = 0
        cdef np.ndarray[unsigned char, ndim=1] occlusion_state = np.zeros(chunk_size**3, dtype=np.ubyte)

        for i in range(chunk_size**3):
            if not voxel_data[i]:
                continue

            x = i / (chunk_size * chunk_size)
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            face_count += self.check_occlusion(chunk_size, x, y, z, i, &occlusion_state[0], &voxel_data[0], &neighbors[0])

        cdef np.ndarray[unsigned int, ndim=1] vertex_data = np.zeros(face_count * 6, dtype=np.uintc)
        cdef int index = 0

        for i in range(chunk_size**3):
            if not occlusion_state[i]:
                continue

            x = i / (chunk_size * chunk_size)
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            side = self.texture_types[voxel_data[i] * 3 - 1]
            up = self.texture_types[voxel_data[i] * 3 - 3]
            down = self.texture_types[voxel_data[i] * 3 - 2]

            occlusion = occlusion_state[i]

            if occlusion >= 32:
                occlusion -= 32
                self.copy_face(index, x, y, z, side, 5, face_5, &vertex_data[0])
                index += 1

            if occlusion >= 16:
                occlusion -= 16
                self.copy_face(index, x, y, z, up, 4, face_4, &vertex_data[0])
                index += 1

            if occlusion >= 8:
                occlusion -= 8
                self.copy_face(index, x, y, z, side, 3, face_3, &vertex_data[0])
                index += 1

            if occlusion >= 4:
                occlusion -= 4
                self.copy_face(index, x, y, z, side, 2, face_2, &vertex_data[0])
                index += 1

            if occlusion >= 2:
                occlusion -= 2
                self.copy_face(index, x, y, z, down, 1, face_1, &vertex_data[0])
                index += 1

            if occlusion >= 1:
                occlusion -= 1
                self.copy_face(index, x, y, z, side, 0, face_0, &vertex_data[0])
                index += 1

        return vertex_data

    cdef void copy_face(self, int index, int x, int y, int z, int texture_id, int normal_id, int* face, unsigned int* vertex_data) noexcept:
        cdef int i, x_position, y_position, z_position

        for i in range(6):
            x_position = face[i * 3 + 0] + x
            y_position = face[i * 3 + 1] + y
            z_position = face[i * 3 + 2] + z

            # pack vertex data into uint32
            vertex_data[index * 6 + i] = x_position | y_position << 6 | z_position << 12 | normal_id << 18 | texture_id << 21

    cdef int check_occlusion(self, int chunk_size, int x, int y, int z, int index, unsigned char* occlusion, unsigned char* voxel_data, long long* neighbor_chunks) noexcept:
        cdef int i, x_position, y_position, z_position, neighbor_id
        cdef int voxel_id = voxel_data[x * chunk_size * chunk_size + y * chunk_size + z]
        cdef int face_count = 0
        cdef unsigned char* neighbor_chunk
        cdef unsigned char result = 0

        for i in range(6):
            x_position = neighbor_offsets[i * 3 + 0] + x
            y_position = neighbor_offsets[i * 3 + 1] + y
            z_position = neighbor_offsets[i * 3 + 2] + z

            if x_position < 0:
                neighbor_chunk = <unsigned char*>neighbor_chunks[0]
                x_position += chunk_size

            elif x_position >= chunk_size:
                neighbor_chunk = <unsigned char*>neighbor_chunks[3]
                x_position -= chunk_size

            elif y_position < 0:
                neighbor_chunk = <unsigned char*>neighbor_chunks[1]
                y_position += chunk_size

            elif y_position >= chunk_size:
                neighbor_chunk = <unsigned char*>neighbor_chunks[4]
                y_position -= chunk_size

            elif z_position < 0:
                neighbor_chunk = <unsigned char*>neighbor_chunks[2]
                z_position += chunk_size

            elif z_position >= chunk_size:
                neighbor_chunk = <unsigned char*>neighbor_chunks[5]
                z_position -= chunk_size

            else:
                neighbor_chunk = voxel_data

            if neighbor_chunk:
                neighbor_id = neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + z_position]

            else:
                continue

            if neighbor_id == voxel_id:
                continue

            if not neighbor_id or not self.occlusion_types[neighbor_id - 1]:
                result += 1 << i
                face_count += 1

        occlusion[index] = result
        return face_count