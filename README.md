# CubePixel

![](./screenshot.png)


## Getting started

Python 3.10+ required

1. Install dependencies using pip:
```
python -m pip install -r requirements.txt
```
2. Build the cython extension:
```
python setup.py build_ext -i
```
- Or if you are using mingw on windows use:
```
python setup.py build_ext --compiler=mingw32 -i
```
3. Run the game:
```
python main.py
```

## Planed features

- Input binding
- Level of detail
- Multithreaded chunk meshing
- Viewmodel
- Structure generation
- Dynamic lighting and shadows
- Water surface and underwater shader
- Multiplayer (maybe)
- Physics (maybe)

## Known Bugs

- loading save files is slow on windows
- collisions break at slow velocity

