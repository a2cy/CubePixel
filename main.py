# ruff: noqa: E402, F401, SIM112
import os
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import AntialiasAttrib, load_prc_file
from ursina import Ursina, Entity, Texture, color, window


def main() -> None:
    os.environ["vblank_mode"] = "0"
    os.environ["__GL_SYNC_TO_VBLANK"] = "0"

    load_prc_file("config.prc")

    # replace builtin for better performance
    Entity.has_disabled_ancestor = lambda self: not self.get_stashed_ancestor().is_empty()

    Texture.default_filtering = "linear"

    app = Ursina(development_mode=False, forced_aspect_ratio=1.778, title="CubePixel")
    window.color = color.black

    msaa_filter = CommonFilters(app.win, app.cam)
    msaa_filter.setMSAA(4)
    app.render.setAntialias(AntialiasAttrib.MMultisample)

    from src.gui import gui  # starts game

    app.run()


if __name__ == "__main__":
    main()
