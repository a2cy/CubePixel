import time

import numpy as np
from data_generator import generate_data
from mesh_generator import generate_mesh

from src.resource_loader import resource_loader

CHUNK_SIZE = 32
RUN_NUM = 36_000

seed = 0
position = (0, 0, 0)

data = generate_data(CHUNK_SIZE, seed, *position)
neighbors = np.zeros(6, dtype=np.longlong)


def test_a():
    for _ in range(RUN_NUM):
        generate_mesh(CHUNK_SIZE, resource_loader.texture_types, resource_loader.occlusion_types, data, neighbors)


def test_b():
    for _ in range(RUN_NUM):
        generate_data(CHUNK_SIZE, seed, *position)


t1 = time.perf_counter()
test_a()
t2 = time.perf_counter()
test_b()
t3 = time.perf_counter()

print(f"Generate mesh without threading {(t2 - t1)}")
print(f"Generate voxel data without threading {(t3 - t2)} \n")
