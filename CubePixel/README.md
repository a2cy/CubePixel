# CubePixel

## Getting Started 
1) Install Python 3.10 or newer.
2) Install the dependencies with `pip install -r requirements.txt`.
3) Copy [FastNoiseLite](https://github.com/Auburn/FastNoiseLite/blob/master/C/FastNoiseLite.h) into [src](/src) and insert `#define FNL_IMPL` on the top
4) Build the cython extension with `python setup.py build_ext --inplace`(you need a c compiler).
5) Run [main.py](main.py).

## Bug/Issues
If you find a bug or you have any issues please let me know by creating an issue.
