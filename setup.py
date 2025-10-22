import numpy as np

from setuptools import setup
from Cython.Build import cythonize


setup(ext_modules=cythonize("./ext/world_tools.pyx"), include_dirs=[np.get_include()])
