"""Semantic room helpers for OpenInteriorCAD."""

from OICDimensions import (
    update_room_dimensions,
)
from OICWall import rebuild_room


ROOM_TYPE = "OpenInteriorCAD::Room"
WALL_TYPE = "OpenInteriorCAD::Wall"


def create_room(
    document,
    name="Room",
):
    """Create an OpenInteriorCAD room group."""

    room = document.addObject(
        "App::DocumentObjectGroup",
        name,
    )

    room.Label = "Pomieszczenie"

    # --------------------------------------------------
    # OPENINTERIORCAD TYPE
    # --------------------------------------------------

    if "OICType" not in room.PropertiesList:
        room.addProperty(
            "App::PropertyString",
            "OICType",
            "OpenInteriorCAD",
            "Semantic object type.",
        )

    # --------------------------------------------------
    # LICZBA ŚCIAN
    # --------------------------------------------------

    if "WallCount" not in room.PropertiesList:
        room.addProperty(
            "App::PropertyInteger",
            "WallCount",
            "OpenInteriorCAD",
            "Liczba ścian pomieszczenia.",
        )

        room.setEditorMode(
            "WallCount",
            1,
        )

    # --------------------------------------------------
    # ZAMKNIĘTY OBWÓD
    # --------------------------------------------------

    if "Closed" not in room.PropertiesList:
        room.addProperty(
            "App::PropertyBool",
            "Closed",
            "OpenInteriorCAD",
            "Czy obrys pomieszczenia jest zamknięty.",
        )

        room.setEditorMode(
            "Closed",
            1,
        )

    # --------------------------------------------------
    # WYMIARY
    # --------------------------------------------------

    if "ShowDimensions" not in room.PropertiesList:
        room.addProperty(
            "App::PropertyBool",
            "ShowDimensions",
            "OpenInteriorCAD",
            "Pokazuje automatyczne wymiary ścian.",
        )

    # --------------------------------------------------
    # POWIERZCHNIA
    # --------------------------------------------------

    if "Area" not in room.PropertiesList:
        room.addProperty(
            "App::PropertyArea",
            "Area",
            "Obliczenia",
            "Powierzchnia pomieszczenia.",
        )

        room.setEditorMode(
            "Area",
            1,
        )

    # --------------------------------------------------
    # OBWÓD
    # --------------------------------------------------

    if "Perimeter" not in room.PropertiesList:
        room.addProperty(
            "App::PropertyLength",
            "Perimeter",
            "Obliczenia",
            "Obwód pomieszczenia.",
        )

        room.setEditorMode(
            "Perimeter",
            1,
        )

    # --------------------------------------------------
    # WARTOŚCI POCZĄTKOWE
    # --------------------------------------------------

    room.OICType = ROOM_TYPE

    room.WallCount = 0
    room.Closed = False

    room.ShowDimensions = True

    room.Area = 0.0
    room.Perimeter = 0.0

    return room


def get_room_walls(
    room,
):
    """Return room walls in drawing order."""

    if room is None:
        return []

    return [
        obj
        for obj in room.Group
        if getattr(
            obj,
            "OICType",
            "",
        )
        == WALL_TYPE
    ]


def add_wall_to_room(
    room,
    wall,
):
    """Add wall to room and rebuild parametric chain."""

    if room is None:
        return

    if wall is None:
        return

    room.addObject(
        wall
    )

    update_room_properties(
        room
    )

    rebuild_room(
        room
    )

    update_room_calculations(
        room
    )

    if room.ShowDimensions:
        update_room_dimensions(
            room
        )


def update_room_properties(
    room,
):
    """Update basic room properties."""

    if room is None:
        return

    walls = get_room_walls(
        room
    )

    room.WallCount = len(
        walls
    )


def update_room_calculations(
    room,
):
    """
    Update room perimeter.

    Area is calculated by OICFloor after the
    floor polygon has been successfully created.
    """

    if room is None:
        return

    walls = get_room_walls(
        room
    )

    perimeter = sum(
        wall.Length.Value
        for wall in walls
    )

    room.Perimeter = perimeter


def update_wall_corners(
    room,
):
    """Enable automatic wall corner extensions."""

    walls = get_room_walls(
        room
    )

    for wall in walls:
        wall.ExtendStart = True
        wall.ExtendEnd = True

    rebuild_room(
        room
    )


def clear_wall_corners(
    room,
):
    """Disable automatic wall corner extensions."""

    walls = get_room_walls(
        room
    )

    for wall in walls:
        wall.ExtendStart = False
        wall.ExtendEnd = False

    rebuild_room(
        room
    )


def close_room(
    room,
):
    """Close room and update its geometry."""

    if room is None:
        return

    update_room_properties(
        room
    )

    room.Closed = True

    update_wall_corners(
        room
    )

    rebuild_room(
        room
    )

    update_room_calculations(
        room
    )

    if room.ShowDimensions:
        update_room_dimensions(
            room
        )


def refresh_room(
    room,
):
    """
    Rebuild complete room after geometry changes.

    This can be used later after wall, door,
    window or floor modifications.
    """

    if room is None:
        return

    update_room_properties(
        room
    )

    rebuild_room(
        room
    )

    update_room_calculations(
        room
    )

    if room.ShowDimensions:
        update_room_dimensions(
            room
        )