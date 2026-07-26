"""Entry point for `iron-rust` and `python -m iron_rust`."""

import sys

# Force UTF-8 output so the box-drawing/arrow glyphs render on any console or
# codepage, instead of crashing on a legacy cp1252 terminal.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from iron_rust.core.game import Game
from iron_rust.ui.dialogue import console


def main():
    game = Game()
    try:
        game.start()
    except (KeyboardInterrupt, EOFError):
        # A Ctrl+C mid-duel shouldn't dump a traceback — bow out gracefully.
        console.print("\n[grey62]You ride off into the dark. So long, partner.[/grey62]")


if __name__ == "__main__":
    main()
