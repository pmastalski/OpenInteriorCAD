"""Central icon paths for OpenInteriorCAD."""

from pathlib import Path


_BASE = Path(__file__).resolve().parent
_ICONS = _BASE / "Resources" / "icons"


def icon(name):
    """Return absolute path to an OpenInteriorCAD SVG icon."""
    return str(_ICONS / name)
