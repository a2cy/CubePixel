from ursina import Ursina, color, window

# from panda3d.core import load_prc_file_data
# load_prc_file_data("", "want-pstats 1")
# load_prc_file_data("", "pstats-python-profiler 1") 

app = Ursina(development_mode=True, forced_aspect_ratio=1.778, borderless=False, title="CubePixel")

window.color = color.black

from src import * # starts game

app.run()