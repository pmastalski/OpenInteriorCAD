"""Parametric floor object for OpenInteriorCAD."""

import FreeCAD as App
import Part


FLOOR_TYPE = "OpenInteriorCAD::Floor"
ROOM_TYPE = "OpenInteriorCAD::Room"
WALL_TYPE = "OpenInteriorCAD::Wall"


def get_room_walls(room):
    """Return walls belonging to a room."""

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


def get_floor_points(room):
    """
    Return polygon points from room walls.

    The wall StartPoints define the closed
    room polygon.
    """

    walls = get_room_walls(
        room
    )

    if len(walls) < 3:
        return []

    points = []

    for wall in walls:
        point = wall.StartPoint

        points.append(
            App.Vector(
                point.x,
                point.y,
                0.0,
            )
        )

    return points


def create_floor_face(room):
    """Create planar face from room wall points."""

    points = get_floor_points(
        room
    )

    if len(points) < 3:
        return None

    # Close polygon.
    polygon_points = list(
        points
    )

    polygon_points.append(
        points[0]
    )

    try:
        wire = Part.makePolygon(
            polygon_points
        )

        face = Part.Face(
            wire
        )

        return face

    except Exception as error:
        App.Console.PrintError(
            "OpenInteriorCAD: nie można utworzyć "
            f"powierzchni podłogi: {error}\n"
        )

        return None

def get_room_floor(room):
    """Return floor assigned to a room."""

    if room is None:
        return None

    document = room.Document

    if document is None:
        return None

    for obj in document.Objects:
        if (
            getattr(
                obj,
                "OICType",
                "",
            )
            != FLOOR_TYPE
        ):
            continue

        if (
            getattr(
                obj,
                "Room",
                None,
            )
            == room
        ):
            return obj

    return None


def rebuild_room_floor(room):
    """Rebuild floor assigned to the room."""

    floor = get_room_floor(
        room
    )

    if floor is None:
        return

    proxy = getattr(
        floor,
        "Proxy",
        None,
    )

    if proxy is None:
        return

    try:
        proxy.rebuild_geometry(
            floor
        )

    except Exception as error:
        App.Console.PrintError(
            "OpenInteriorCAD: błąd "
            "aktualizacji podłogi: "
            f"{error}\n"
        )


def calculate_room_perimeter(room):
    """Calculate room perimeter from walls."""

    walls = get_room_walls(
        room
    )

    return sum(
        wall.Length.Value
        for wall in walls
    )


def update_room_properties(room):
    """Update calculated room properties."""

    face = create_floor_face(
        room
    )

    if face is None:
        return

    area_mm2 = face.Area

    perimeter_mm = (
        calculate_room_perimeter(
            room
        )
    )

    if "Area" in room.PropertiesList:
        room.Area = area_mm2

    if "Perimeter" in room.PropertiesList:
        room.Perimeter = perimeter_mm


class FloorProxy:
    """Parametric floor generated from a room."""

    TYPE_ID = FLOOR_TYPE

    def __init__(
        self,
        obj,
        room=None,
        thickness=20.0,
    ):
        self._add_properties(
            obj
        )

        obj.Proxy = self

        if room is not None:
            obj.Room = room

        obj.Thickness = thickness

        self.rebuild_geometry(
            obj
        )

    def _add_properties(
        self,
        obj,
    ):
        """Create floor properties."""

        if "OICType" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyString",
                "OICType",
                "OpenInteriorCAD",
                "Semantic object type.",
            )

        if "Room" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLink",
                "Room",
                "Podłoga",
                "Pomieszczenie przypisane do podłogi.",
            )

        if "Thickness" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Thickness",
                "Podłoga",
                "Grubość podłogi.",
            )

        if "Area" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyArea",
                "Area",
                "Obliczenia",
                "Powierzchnia podłogi.",
            )

            obj.setEditorMode(
                "Area",
                1,
            )

        if "Perimeter" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Perimeter",
                "Obliczenia",
                "Obwód podłogi.",
            )

            obj.setEditorMode(
                "Perimeter",
                1,
            )

        obj.OICType = self.TYPE_ID

    def rebuild_geometry(
        self,
        obj,
    ):
        """Rebuild floor geometry."""

        room = obj.Room

        if room is None:
            obj.Shape = Part.Shape()
            return

        face = create_floor_face(
            room
        )

        if face is None:
            obj.Shape = Part.Shape()
            return

        thickness = max(
            1.0,
            obj.Thickness.Value,
        )

        try:
            # Extrude downward so floor top remains Z=0.
            shape = face.extrude(
                App.Vector(
                    0.0,
                    0.0,
                    -thickness,
                )
            )

            obj.Shape = shape

            obj.Area = face.Area

            obj.Perimeter = (
                calculate_room_perimeter(
                    room
                )
            )

            update_room_properties(
                room
            )

        except Exception as error:
            obj.Shape = Part.Shape()

            App.Console.PrintError(
                "OpenInteriorCAD: błąd budowania "
                f"podłogi: {error}\n"
            )

    def execute(
        self,
        obj,
    ):
        self.rebuild_geometry(
            obj
        )

    def onChanged(
        self,
        obj,
        property_name,
    ):
        if property_name not in {
            "Room",
            "Thickness",
        }:
            return

        required = {
            "Room",
            "Thickness",
        }

        if not required.issubset(
            set(
                obj.PropertiesList
            )
        ):
            return

        try:
            self.rebuild_geometry(
                obj
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD floor update error: "
                f"{error}\n"
            )

    def onDocumentRestored(
        self,
        obj,
    ):
        self._add_properties(
            obj
        )

        obj.Proxy = self


class FloorViewProvider:
    """View provider for OpenInteriorCAD floor."""

    def __init__(
        self,
        view_object,
    ):
        view_object.Proxy = self

    def attach(
        self,
        view_object,
    ):
        return

    def updateData(
        self,
        obj,
        property_name,
    ):
        return

    def getDisplayModes(
        self,
        view_object,
    ):
        return []

    def getDefaultDisplayMode(
        self,
    ):
        return "Flat Lines"

    def setDisplayMode(
        self,
        mode,
    ):
        return mode

    def onChanged(
        self,
        view_object,
        property_name,
    ):
        return

    def dumps(
        self,
    ):
        return None

    def loads(
        self,
        state,
    ):
        return None


def create_floor(
    document,
    room,
    thickness=20.0,
    name="Floor",
):
    """Create floor for an OpenInteriorCAD room."""

    obj = document.addObject(
        "Part::FeaturePython",
        name,
    )

    obj.Label = "Podłoga"

    FloorProxy(
        obj,
        room=room,
        thickness=thickness,
    )

    FloorViewProvider(
        obj.ViewObject
    )

    document.recompute()

    try:
        obj.ViewObject.ShapeColor = (
            0.72,
            0.62,
            0.45,
        )

        obj.ViewObject.Transparency = 15

    except Exception:
        pass

    obj.ViewObject.Visibility = True

    return obj