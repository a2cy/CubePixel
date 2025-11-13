# cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
from fast_noise_lite cimport *

cimport numpy as np
import numpy as np


np.import_array()

cdef float amp2d = 32
cdef int y_offset = 12
cdef fnl_state noise2d = fnlCreateState()

noise2d.noise_type = FNL_NOISE_OPENSIMPLEX2
noise2d.fractal_type = FNL_FRACTAL_FBM
noise2d.frequency = 0.002
noise2d.gain = 1
noise2d.octaves = 4


def generate_data(int chunk_size, int seed, int chunk_x, int chunk_y, int chunk_z):
    cdef int i, index, x, y, z, world_y, diff, height
    cdef np.ndarray[unsigned char, ndim=1] voxel_data = np.zeros(chunk_size**3, dtype=np.ubyte)
    noise2d.seed = seed

    for i in range(chunk_size**2):
        x = i / chunk_size
        z = i % chunk_size
        height = <int>(fnlGetNoise2D(&noise2d, x + chunk_x, z + chunk_z) * amp2d + y_offset)

        for y in range(chunk_size):
            index = x * chunk_size * chunk_size + y * chunk_size + z
            world_y = y + chunk_y
            diff = height - world_y

            if diff == 0 and world_y >= 0:
                voxel_data[index] = 2  # grass

            elif diff < 5 and diff >= 0:
                voxel_data[index] = 1  # dirt

            elif diff >= 5:
                voxel_data[index] = 3  # stone

            if world_y <= 0 and diff < 0:
                voxel_data[index] = 5  # water

    return voxel_data
