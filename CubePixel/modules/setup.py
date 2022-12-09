import numpy as np

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("./modules/cython_functions.pyx", language_level=3),
    include_dirs=[np.get_include()]
) 
