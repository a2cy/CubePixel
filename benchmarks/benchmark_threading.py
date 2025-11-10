import time
import threading
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


def test_a_threading():
    threads = []
    for _ in range(RUN_NUM):
        thread = threading.Thread(target=world_generator.generate_mesh, args=(CHUNK_SIZE, data, neighbors))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def test_b_threading():
    threads = []
    for _ in range(RUN_NUM):
        thread = threading.Thread(target=world_generator.generate_voxels, args=(CHUNK_SIZE, seed, *position))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


t1 = time.perf_counter()
test_a_threading()
t2 = time.perf_counter()
test_b_threading()
t3 = time.perf_counter()

print(f"Generate mesh with threading {(t2 - t1)}")
print(f"Generate voxel data with threading {(t3 - t2)} \n")
