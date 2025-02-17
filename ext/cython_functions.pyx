# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True, cpow=True
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
from fast_noise_lite cimport *

cimport numpy as np
import numpy as np


np.import_array()


cdef float[18] face_0 = [0, 0, 0,
                         1, 0, 0,
                         1, 1, 0,
                         1, 1, 0,
                         0, 1, 0,
                         0, 0, 0,]

cdef float[18] face_1 = [0, 0, 0,
                         0, 0, 1,
                         1, 0, 1,
                         1, 0, 1,
                         1, 0, 0,
                         0, 0, 0,]

cdef float[18] face_2 = [0, 0, 0,
                         0, 1, 0,
                         0, 1, 1,
                         0, 1, 1,
                         0, 0, 1,
                         0, 0, 0,]

cdef float[18] face_3 = [0, 0, 1,
                         0, 1, 1,
                         1, 1, 1,
                         1, 1, 1,
                         1, 0, 1,
                         0, 0, 1,]

cdef float[18] face_4 = [0, 1, 0,
                         1, 1, 0,
                         1, 1, 1,
                         1, 1, 1,
                         0, 1, 1,
                         0, 1, 0,]

cdef float[18] face_5 = [1, 0, 0,
                         1, 0, 1,
                         1, 1, 1,
                         1, 1, 1,
                         1, 1, 0,
                         1, 0, 0,]


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

        cdef np.ndarray[unsigned short, ndim=1] voxel_data = np.zeros(chunk_size**3, dtype=np.ushort)

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


    def generate_mesh(self, unsigned short chunk_size, unsigned short [:] voxel_data, long long [:] neighbors):
        cdef int i, x, y, z, occlusion
        cdef VoxelType voxel

        cdef np.ndarray[unsigned short, ndim=1] occlusion_state = np.zeros(chunk_size**3, dtype=np.ushort)
        cdef int face_count = 0

        for i in range(chunk_size**3):
            if not voxel_data[i]:
                continue

            x = i / chunk_size / chunk_size
            y = i / chunk_size % chunk_size
            z = i % chunk_size

            face_count += self.check_occlusion(chunk_size, x, y, z, i, &occlusion_state[0], &voxel_data[0], &neighbors[0])

        cdef np.ndarray[float, ndim=1] vertices = np.zeros(18 * face_count, dtype=np.single)
        cdef np.ndarray[unsigned short, ndim=1] vertex_data = np.zeros(12 * face_count, dtype=np.ushort)

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
                self.copy_face(index, x, y, z, face_5, voxel.side, 5, &vertices[0], &vertex_data[0])
                index += 1

            if occlusion >= 16:
                occlusion -= 16
                self.copy_face(index, x, y, z, face_4, voxel.up, 4, &vertices[0], &vertex_data[0])
                index += 1

            if occlusion >= 8:
                occlusion -= 8
                self.copy_face(index, x, y, z, face_3, voxel.side, 3, &vertices[0], &vertex_data[0])
                index += 1

            if occlusion >= 4:
                occlusion -= 4
                self.copy_face(index, x, y, z, face_2, voxel.side, 2, &vertices[0], &vertex_data[0])
                index += 1

            if occlusion >= 2:
                occlusion -= 2
                self.copy_face(index, x, y, z, face_1, voxel.down, 1, &vertices[0], &vertex_data[0])
                index += 1

            if occlusion >= 1:
                occlusion -= 1
                self.copy_face(index, x, y, z, face_0, voxel.side, 0, &vertices[0], &vertex_data[0])
                index += 1

        return [vertices, vertex_data]


    cdef void copy_face(self, int index, int x, int y, int z, float* face, unsigned short texture_id, unsigned short normal_id, float* vertices, unsigned short* vertex_data):
        cdef int i

        for i in range(6):
            vertices[index * 18 + i * 3 + 0] = face[i * 3 + 0] + x
            vertices[index * 18 + i * 3 + 1] = face[i * 3 + 1] + y
            vertices[index * 18 + i * 3 + 2] = face[i * 3 + 2] + z

        for i in range(6):
            vertex_data[index * 12 + i * 2 + 0] = texture_id
            vertex_data[index * 12 + i * 2 + 1] = normal_id


    cdef int check_occlusion(self, unsigned short chunk_size, int x, int y, int z, int index, unsigned short* occlusion, unsigned short* voxel_data, long long* neighbor_chunks):
        cdef int i, x_position, y_position, z_position, voxel_id
        cdef unsigned short* neighbor_chunk

        cdef unsigned short result = 0
        cdef int face_count = 0

        for i in range(3 * 2):
            x_position = (i + 0) % 3 / 2 * (i / 3 * 2 - 1) + x
            y_position = (i + 1) % 3 / 2 * (i / 3 * 2 - 1) + y
            z_position = (i + 2) % 3 / 2 * (i / 3 * 2 - 1) + z

            voxel_id = -1

            if x_position < 0:
                neighbor_chunk = <unsigned short*>neighbor_chunks[2]

                if neighbor_chunk:
                    voxel_id = neighbor_chunk[(x_position + chunk_size) * chunk_size * chunk_size + y_position * chunk_size + z_position]

            elif x_position >= chunk_size:
                neighbor_chunk = <unsigned short*>neighbor_chunks[5]

                if neighbor_chunk:
                    voxel_id = neighbor_chunk[(x_position - chunk_size) * chunk_size * chunk_size + y_position * chunk_size + z_position]

            elif y_position < 0:
                neighbor_chunk = <unsigned short*>neighbor_chunks[1]

                if neighbor_chunk:
                    voxel_id = neighbor_chunk[x_position * chunk_size * chunk_size + (y_position + chunk_size) * chunk_size + z_position]

            elif y_position >= chunk_size:
                neighbor_chunk = <unsigned short*>neighbor_chunks[4]

                if neighbor_chunk:
                    voxel_id = neighbor_chunk[x_position * chunk_size * chunk_size + (y_position - chunk_size) * chunk_size + z_position]

            elif z_position < 0:
                neighbor_chunk = <unsigned short*>neighbor_chunks[0]

                if neighbor_chunk:
                    voxel_id = neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + (z_position + chunk_size)]

            elif z_position >= chunk_size:
                neighbor_chunk = <unsigned short*>neighbor_chunks[3]

                if neighbor_chunk:
                    voxel_id = neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + (z_position - chunk_size)]

            else:
                voxel_id = voxel_data[x_position * chunk_size * chunk_size + y_position * chunk_size + z_position]

            if voxel_id < 0:
                continue

            if voxel_id == voxel_data[x * chunk_size * chunk_size + y * chunk_size + z]:
                continue

            if not voxel_id:
                result += 2**i
                face_count += 1

            elif self.voxel_types[voxel_id - 1].occlusion == False:
                result += 2**i
                face_count += 1

        occlusion[index] = result
        return face_count