import threading
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

threads_a = []
for _ in range(RUN_NUM):
    thread = threading.Thread(
        target=generate_mesh, args=(CHUNK_SIZE, resource_loader.texture_types, resource_loader.occlusion_types, data, neighbors)
    )
    threads_a.append(thread)


def test_a_threading():
    for thread in threads_a:
        thread.start()

    for thread in threads_a:
        thread.join()


threads_b = []
for _ in range(RUN_NUM):
    thread = threading.Thread(target=generate_data, args=(CHUNK_SIZE, seed, *position))
    threads_b.append(thread)


def test_b_threading():
    for thread in threads_b:
        thread.start()

    for thread in threads_b:
        thread.join()


t1 = time.perf_counter()
test_a_threading()
t2 = time.perf_counter()
test_b_threading()
t3 = time.perf_counter()

print(f"Generate mesh with threading {(t2 - t1)}")
print(f"Generate voxel data with threading {(t3 - t2)} \n")
