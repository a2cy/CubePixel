# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION


from fast_noise_lite cimport fnl_state, FNL_NOISE_OPENSIMPLEX2, FNL_FRACTAL_FBM, fnlCreateState, fnlGetNoise2D

cimport numpy as np
import numpy as np


np.import_array()


cdef class VoxelType:
    cdef public unsigned int shape
    cdef public float [:] vertices
    cdef public float [:] uvs
    cdef public char occlusion
    cdef public char collision


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

        cdef float amp2d = 16

        cdef unsigned short air = voxel_index["air"]
        cdef unsigned short dirt = voxel_index["dirt"]
        cdef unsigned short grass = voxel_index["grass"]
        cdef unsigned short stone = voxel_index["stone"]

        self.noise2d.seed = seed
        self.noise2d.frequency = 0.01
        self.noise2d.gain = 0.5
        self.noise2d.octaves = 3

        cdef np.ndarray[unsigned short, ndim=1] voxel_data = np.zeros(chunk_size**3, dtype=np.ushort)

        for i in range(chunk_size**2):
            x = i // chunk_size
            z = i % chunk_size

            max_y = <int>(fnlGetNoise2D(&self.noise2d, x + position[0], z + position[2]) * amp2d + amp2d / 2)

            for y in range(chunk_size):
                i = x * chunk_size * chunk_size + y * chunk_size + z
                y = y + position[1]
                diff = max_y - y

                if diff == 0:
                    voxel_data[i] = grass

                elif diff < 5 and diff > 0:
                    voxel_data[i] = dirt

                elif diff >= 5:
                    voxel_data[i] = stone

                else:
                    voxel_data[i] = air

        return voxel_data


    def combine_mesh(self, unsigned short chunk_size , int [:] position, unsigned short [:] voxel_data, long long [:] neighbors):
        cdef int i, shape, vertex_count = 0
        cdef int[3] voxel_position
        cdef np.ndarray[int, ndim=1] indices = np.zeros((chunk_size**3), dtype=np.intc)
        cdef VoxelType voxel

        for i in range(chunk_size**3):
            shape = self.voxel_types[voxel_data[i]].shape

            if shape == 0:
                indices[i] = -1
                continue

            voxel_position[0] = i / chunk_size / chunk_size
            voxel_position[1] = i / chunk_size % chunk_size
            voxel_position[2] = i % chunk_size % chunk_size

            if self.check_occlusion(chunk_size, voxel_position, &voxel_data[0], &neighbors[0]):
                indices[i] = -1
                continue

            indices[i] = vertex_count

            vertex_count += shape

        cdef np.ndarray[float, ndim=1] vertices = np.zeros((vertex_count*3), dtype=np.single)
        cdef np.ndarray[float, ndim=1] uvs = np.zeros((vertex_count*3), dtype=np.single)

        if vertex_count == 0:
            return [vertices, uvs]

        for i in range(chunk_size**3):
            if indices[i] == -1:
                continue

            voxel_position[0] = i / chunk_size / chunk_size + position[0]
            voxel_position[1] = i / chunk_size % chunk_size + position[1]
            voxel_position[2] = i % chunk_size % chunk_size + position[2]

            voxel = self.voxel_types[voxel_data[i]]

            self.translate(voxel.shape, indices[i], &voxel.vertices[0], voxel_position, &vertices[0])
            self.translate(voxel.shape, indices[i], &voxel.uvs[0], [0, 0, 0], &uvs[0])

        return [vertices, uvs]


    cdef translate(self, unsigned int shape, unsigned int index, float* data, int* position, float* result):
        cdef unsigned int i

        for i in range(shape):
            result[i*3 + index*3 + 0] = data[i*3 + 0] + position[0]
            result[i*3 + index*3 + 1] = data[i*3 + 1] + position[1]
            result[i*3 + index*3 + 2] = data[i*3 + 2] + position[2]


    cdef check_occlusion(self, unsigned short chunk_size, int* position, unsigned short* voxel_data, long long* neighbor_chunks):
        cdef int x_position, y_position, z_position
        cdef unsigned int i
        cdef unsigned short* neighbor_chunk

        cdef VoxelType neighbor

        for i in range(3 * 2):
            x_position = (i + 0) % 3 / 2 * (i / 3 * 2 - 1) + position[0]
            y_position = (i + 1) % 3 / 2 * (i / 3 * 2 - 1) + position[1]
            z_position = (i + 2) % 3 / 2 * (i / 3 * 2 - 1) + position[2]

            if x_position < 0:
                neighbor_chunk = <unsigned short*>neighbor_chunks[2]
                if neighbor_chunk:
                    neighbor = self.voxel_types[neighbor_chunk[(x_position + chunk_size) * chunk_size * chunk_size + y_position * chunk_size + z_position]]

                    if neighbor.occlusion == False:
                        return False

                continue

            if x_position >= chunk_size:
                neighbor_chunk = <unsigned short*>neighbor_chunks[5]

                if neighbor_chunk:
                    neighbor = self.voxel_types[neighbor_chunk[(x_position - chunk_size) * chunk_size * chunk_size + y_position * chunk_size + z_position]]

                    if neighbor.occlusion == False:
                        return False

                continue

            if y_position < 0:
                neighbor_chunk = <unsigned short*>neighbor_chunks[1]

                if neighbor_chunk:
                    neighbor = self.voxel_types[neighbor_chunk[x_position * chunk_size * chunk_size + (y_position + chunk_size) * chunk_size + z_position]]

                    if neighbor.occlusion == False:
                        return False

                continue

            if y_position >= chunk_size:
                neighbor_chunk = <unsigned short*>neighbor_chunks[4]

                if neighbor_chunk:
                    neighbor = self.voxel_types[neighbor_chunk[x_position * chunk_size * chunk_size + (y_position - chunk_size) * chunk_size + z_position]]

                    if neighbor.occlusion == False:
                        return False

                continue

            if z_position < 0:
                neighbor_chunk = <unsigned short*>neighbor_chunks[0]

                if neighbor_chunk:
                    neighbor = self.voxel_types[neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + (z_position + chunk_size)]]

                    if neighbor.occlusion == False:
                        return False

                continue

            if z_position >= chunk_size:
                neighbor_chunk = <unsigned short*>neighbor_chunks[3]

                if neighbor_chunk:
                    neighbor = self.voxel_types[neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + (z_position - chunk_size)]]

                    if neighbor.occlusion == False:
                        return False

                continue

            neighbor = self.voxel_types[voxel_data[x_position * chunk_size * chunk_size + y_position * chunk_size + z_position]]

            if neighbor.occlusion == False:
                return False

        return True
