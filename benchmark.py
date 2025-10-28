import timeit
import numpy as np

from src.resource_loader import resource_loader
from world_tools import WorldGenerator

CHUNK_SIZE = 32
RUN_NUM = 10000

seed = 0
position = (0, 0, 0)

world_generator = WorldGenerator(resource_loader.texture_types, resource_loader.occlusion_types)

data = world_generator.generate_voxels(CHUNK_SIZE, seed, *position)
neighbors = np.zeros(6, dtype=np.longlong)


def test_a():
    world_generator.generate_mesh(CHUNK_SIZE, data, neighbors)


def test_b():
    world_generator.generate_voxels(CHUNK_SIZE, seed, *position)


print(f"Generate mesh {(timeit.timeit(test_a, number=RUN_NUM) / RUN_NUM) * 1000000} µs")
print(f"Generate voxel data {(timeit.timeit(test_b, number=RUN_NUM) / RUN_NUM) * 1000000} µs")

"""
Results
seed = 0
position = (0, 0, 0)
Generate mesh 180 µs
Generate voxel data 60 µs
"""
