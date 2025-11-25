# ruff: noqa: E402, F401, SIM112
import os
from panda3d.core import load_prc_file
from ursina import Ursina, Entity, color, window


def main() -> None:
    os.environ["vblank_mode"] = "0"
    os.environ["__GL_SYNC_TO_VBLANK"] = "0"

    load_prc_file("config.prc")

    # replace builtin for better performance
    Entity.has_disabled_ancestor = lambda self: not self.get_stashed_ancestor().is_empty()

    app = Ursina(development_mode=False, forced_aspect_ratio=1.778, title="CubePixel")
    window.color = color.black

    from src.gui import gui  # starts game

    app.run()


if __name__ == "__main__":
    main()
