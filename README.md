# CubePixel

## Getting started

Python 3.10+ required

1. Install dependencies using pip:
```
pip install -r requirements.txt
```
2. Build the cython extension ([build tools for windows](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)):
```
python setup.py build_ext -i
```
3. Run the game:
```
python main.py
```

## Known Bugs

- loading save files is slow on windows
