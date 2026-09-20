"""Tall cabinet independent stacked openings; heights are CLEAR heights (mm).

A single row with height 0 is the flexible remainder. JSON is intentionally
stored on the Furniture object so documents survive save/restore and duplication.
"""
import json

ZONE_TYPES = ("Open", "Oven", "Microwave", "Single Door", "Double Door", "Drawers", "Lift-up")


def example_zones():
    return [
        {"type": "Drawers", "height": 440.0, "drawers": 3},
        {"type": "Oven", "height": 600.0, "drawers": 1},
        {"type": "Microwave", "height": 380.0, "drawers": 1},
        {"type": "Single Door", "height": 0.0, "drawers": 1},
    ]


def decode(raw):
    if not raw:
        return []
    try:
        value = json.loads(raw)
        if not isinstance(value, list) or len(value) > 20:
            return []
        result = []
        for row in value:
            kind = str(row.get("type", "Open"))
            if kind not in ZONE_TYPES:
                return []
            height = float(row.get("height", 0))
            count = int(row.get("drawers", 1))
            if height < 0 or height > 10000 or not 1 <= count <= 12:
                return []
            # Preserve manual front divisions when the zone table is edited,
            # moved or saved. A stale drawer count falls back to equal fronts.
            raw_heights = row.get("drawer_heights", [])
            from OICDrawerLayout import decode as decode_drawers
            drawer_heights = decode_drawers(raw_heights)
            result.append({"type": kind, "height": height,
                           "drawers": count, "drawer_heights": drawer_heights})
        return result
    except (TypeError, ValueError, AttributeError):
        return []


def layout(raw, cabinet_height, plinth_height, panel_thickness):
    """Return zones as (row, clear_bottom_z, clear_height), bottom to top.

    Invalid layouts return [] rather than producing overlapping panels. At most
    one automatic-height zone is supported.
    """
    rows = decode(raw)
    if not rows:
        return []
    t = float(panel_thickness)
    inner = float(cabinet_height) - float(plinth_height) - 2 * t
    available = inner - (len(rows) - 1) * t
    if available <= 0:
        return []
    fixed = sum(row["height"] for row in rows if row["height"] > 0)
    autos = [row for row in rows if row["height"] == 0]
    if len(autos) > 1 or (autos and available - fixed < 40) or (not autos and abs(fixed - available) > 0.05):
        return []
    z = float(plinth_height) + t
    result = []
    for row in rows:
        h = available - fixed if row["height"] == 0 else row["height"]
        if h < 40:
            return []
        result.append((row, z, h))
        z += h + t
    return result


def front_bounds(zones, index, panel_thickness, front_gap):
    """Z envelope of one zone front; fronts overlap horizontal dividers.

    The outermost fronts overlay bottom/top boards, while adjacent fronts
    split intermediate divider coverage at its midpoint with a front gap.
    """
    _row, z, h = zones[index]
    t = float(panel_thickness)
    g = float(front_gap)
    bottom = z - t + g if index == 0 else z - t / 2.0 + g / 2.0
    top = z + h + t - g if index == len(zones) - 1 else z + h + t / 2.0 - g / 2.0
    return bottom, max(0.0, top - bottom)
