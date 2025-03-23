# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
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


cdef class VoxelType:
    cdef public unsigned int up
    cdef public unsigned int down
    cdef public unsigned int side
    cdef public bint occlusion
    cdef public bint collision
    cdef public bint inventory


cdef class WorldGenerator:

    cdef VoxelType [:] voxel_types

    cdef fnl_state noise2d


    def __init__(self, VoxelType [:] voxel_types):
        self.voxel_types = voxel_types

        self.noise2d = fnlCreateState()
        self.noise2d.noise_type = FNL_NOISE_OPENSIMPLEX2
        self.noise2d.fractal_type = FNL_FRACTAL_FBM


    def generate_voxels(self, unsigned short chunk_size, dict voxel_index, int seed, int [:] position):
        cdef int i, x, y, z, max_y

        cdef float amp2d = 32

        cdef unsigned short dirt = voxel_index["dirt"]
        cdef unsigned short grass = voxel_index["grass"]
        cdef unsigned short stone = voxel_index["stone"]

        self.noise2d.seed = seed
        self.noise2d.frequency = 0.002
        self.noise2d.gain = 1
        self.noise2d.octaves = 4

        cdef np.ndarray[unsigned char, ndim=1] voxel_data = np.zeros(chunk_size**3, dtype=np.ubyte)

        for i in range(chunk_size**2):
            x = i // chunk_size
            z = i % chunk_size

            max_y = <int>(fnlGetNoise2D(&self.noise2d, x + position[0], z + position[2]) * amp2d + amp2d / 2)

            for y in range(chunk_size):
                i = x * chunk_size * chunk_size + y * chunk_size + z
                diff = max_y - (y + position[1])

                if diff == 0:
                    voxel_data[i] = grass

                elif diff < 5 and diff > 0:
                    voxel_data[i] = dirt

                elif diff >= 5:
                    voxel_data[i] = stone

        return voxel_data


    def generate_mesh(self, unsigned short chunk_size, unsigned char [:] voxel_data, long long [:] neighbors):
        cdef int i, x, y, z, occlusion
        cdef VoxelType voxel

        cdef np.ndarray[unsigned char, ndim=1] occlusion_state = np.zeros(chunk_size**3, dtype=np.ubyte)
        cdef int face_count = 0

        for i in range(chunk_size**3):
            if not voxel_data[i]:
                continue

            x = i / chunk_size / chunk_size
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            face_count += self.check_occlusion(chunk_size, x, y, z, i, &occlusion_state[0], &voxel_data[0], &neighbors[0])

        cdef np.ndarray[unsigned int, ndim=1] vertex_data = np.zeros(face_count * 6, dtype=np.uintc)

        cdef int index = 0

        for i in range(chunk_size**3):
            if not occlusion_state[i]:
                continue

            x = i / chunk_size / chunk_size
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            voxel = self.voxel_types[voxel_data[i] - 1]

            occlusion = occlusion_state[i]

            if occlusion >= 32:
                occlusion -= 32
                self.copy_face(index, x, y, z, voxel.side, 5, face_5, &vertex_data[0])
                index += 1

            if occlusion >= 16:
                occlusion -= 16
                self.copy_face(index, x, y, z, voxel.up, 4, face_4, &vertex_data[0])
                index += 1

            if occlusion >= 8:
                occlusion -= 8
                self.copy_face(index, x, y, z, voxel.side, 3, face_3, &vertex_data[0])
                index += 1

            if occlusion >= 4:
                occlusion -= 4
                self.copy_face(index, x, y, z, voxel.side, 2, face_2, &vertex_data[0])
                index += 1

            if occlusion >= 2:
                occlusion -= 2
                self.copy_face(index, x, y, z, voxel.down, 1, face_1, &vertex_data[0])
                index += 1

            if occlusion >= 1:
                occlusion -= 1
                self.copy_face(index, x, y, z, voxel.side, 0, face_0, &vertex_data[0])
                index += 1

        return vertex_data


    cdef void copy_face(self, int index, int x, int y, int z, int texture_id, int normal_id, int* face, unsigned int* vertex_data):
        cdef int i
        cdef unsigned int data

        for i in range(6):
            data = face[i * 3 + 0] + x
            data = data | ((face[i * 3 + 1] + y) << 6)
            data = data | ((face[i * 3 + 2] + z) << 12)

            data = data | (normal_id << 18)
            data = data | (texture_id << 21)

            vertex_data[index * 6 + i] = data

    cdef int check_occlusion(self, unsigned short chunk_size, int x, int y, int z, int index, unsigned char* occlusion, unsigned char* voxel_data, long long* neighbor_chunks):
        cdef int i, x_position, y_position, z_position, neighbor_id
        cdef unsigned char* neighbor_chunk

        cdef unsigned char result = 0
        cdef int face_count = 0

        cdef int voxel_id = voxel_data[x * chunk_size * chunk_size + y * chunk_size + z]
        cdef int[6][3] neighbor_offsets = [[-1, 0, 0], [0, -1, 0], [0, 0, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]

        for i in range(6):
            x_position = neighbor_offsets[i][0] + x
            y_position = neighbor_offsets[i][1] + y
            z_position = neighbor_offsets[i][2] + z

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

            if not neighbor_id or self.voxel_types[neighbor_id - 1].occlusion == False:
                result += 1 << i
                face_count += 1

        occlusion[index] = result
        return face_count