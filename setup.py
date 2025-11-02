import numpy as np

from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="world_tools",
        sources=["./ext/world_tools.pyx"],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

setup(ext_modules=cythonize(extensions), include_dirs=[np.get_include()])
