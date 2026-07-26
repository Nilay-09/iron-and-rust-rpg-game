"""Load town ASCII art bundled as package data in iron_rust/assets/ascii/."""

from importlib.resources import files

_cache = {}


def load_art(name):
    """Return the ASCII art for a town key, or '' if there's no file for it."""
    if name in _cache:
        return _cache[name]

    art = ""
    try:
        resource = files("iron_rust").joinpath("assets", "ascii", f"{name}.txt")
        if resource.is_file():
            art = resource.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        art = ""

    _cache[name] = art
    return art
