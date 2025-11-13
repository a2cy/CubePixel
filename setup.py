# ruff: noqa I

import numpy as np
from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        name="data_generator",
        sources=["src/data_generator.pyx"],
        include_dirs=["lib/"],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"), ("FNL_IMPL", "")],
    ),
    Extension(
        name="mesh_generator",
        sources=["src/mesh_generator.pyx"],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    ),
]

setup(ext_modules=cythonize(extensions), include_dirs=[np.get_include()], inplace=True)
