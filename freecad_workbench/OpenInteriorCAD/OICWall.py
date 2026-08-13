"""Parametric OpenInteriorCAD wall object."""

import math

import FreeCAD as App
import Part


REFERENCE_AXIS = "Oś"
REFERENCE_LEFT = "Lewa krawędź"
REFERENCE_RIGHT = "Prawa krawędź"

REFERENCE_OPTIONS = [
    REFERENCE_AXIS,
    REFERENCE_LEFT,
    REFERENCE_RIGHT,
]

WALL_TYPE = "OpenInteriorCAD::Wall"
ROOM_TYPE = "OpenInteriorCAD::Room"

DOOR_TYPE = "OpenInteriorCAD::Door"
WINDOW_TYPE = "OpenInteriorCAD::Window"

_REBUILDING = False


def normalize_angle(angle):
    """Normalize angle to -180..180 degrees."""

    return (
        angle + 180.0
    ) % 360.0 - 180.0


def get_wall_doors(wall):
    """Return all doors hosted by a wall."""

    document = wall.Document

    if document is None:
        return []

    return [
        obj
        for obj in document.Objects
        if (
            getattr(
                obj,
                "OICType",
                "",
            )
            == DOOR_TYPE
            and getattr(
                obj,
                "HostWall",
                None,
            )
            == wall
        )
    ]


def get_wall_windows(wall):
    """Return all windows hosted by a wall."""

    document = wall.Document

    if document is None:
        return []

    return [
        obj
        for obj in document.Objects
        if (
            getattr(
                obj,
                "OICType",
                "",
            )
            == WINDOW_TYPE
            and getattr(
                obj,
                "HostWall",
                None,
            )
            == wall
        )
    ]


def build_wall_shape(
    start_point,
    heading,
    length,
    thickness,
    height,
    reference_line,
    extend_start=False,
    extend_end=False,
    doors=None,
    windows=None,
):
    """Build wall solid with door and window openings."""

    if length <= 0.001:
        return Part.Shape()

    if thickness <= 0.001:
        return Part.Shape()

    if height <= 0.001:
        return Part.Shape()

    # --------------------------------------------------
    # PRZEDŁUŻENIA ŚCIANY W NAROŻNIKACH
    # --------------------------------------------------

    start_extension = (
        thickness / 2.0
        if extend_start
        else 0.0
    )

    end_extension = (
        thickness / 2.0
        if extend_end
        else 0.0
    )

    solid_length = (
        length
        + start_extension
        + end_extension
    )

    angle_rad = math.radians(
        heading
    )

    unit_x = math.cos(
        angle_rad
    )

    unit_y = math.sin(
        angle_rad
    )

    extended_start = App.Vector(
        start_point.x
        - unit_x * start_extension,
        start_point.y
        - unit_y * start_extension,
        start_point.z,
    )

    # --------------------------------------------------
    # LINIA ODNIESIENIA
    # --------------------------------------------------

    if reference_line == REFERENCE_LEFT:
        y_offset = 0.0

    elif reference_line == REFERENCE_RIGHT:
        y_offset = -thickness

    else:
        y_offset = -thickness / 2.0

    # --------------------------------------------------
    # GŁÓWNA BRYŁA ŚCIANY
    # --------------------------------------------------

    shape = Part.makeBox(
        solid_length,
        thickness,
        height,
        App.Vector(
            0.0,
            y_offset,
            0.0,
        ),
    )

    # Cutter jest trochę głębszy niż ściana,
    # żeby operacja boolean była stabilniejsza.

    cutter_margin = 10.0

    cutter_y = (
        y_offset
        - cutter_margin
    )

    cutter_depth = (
        thickness
        + 2.0 * cutter_margin
    )

    # ==================================================
    # DRZWI
    # ==================================================

    if doors is None:
        doors = []

    for door in doors:
        try:
            width = door.Width.Value
            opening_height = door.Height.Value
            offset = door.Offset.Value

        except Exception:
            continue

        if width <= 0.001:
            continue

        if opening_height <= 0.001:
            continue

        if offset < 0.0:
            continue

        if offset + width > length:
            continue

        cutter_x = (
            start_extension
            + offset
        )

        cutter = Part.makeBox(
            width,
            cutter_depth,
            opening_height,
            App.Vector(
                cutter_x,
                cutter_y,
                0.0,
            ),
        )

        try:
            shape = shape.cut(
                cutter
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD: błąd wycinania "
                f"drzwi {door.Label}: {error}\n"
            )

    # ==================================================
    # OKNA
    # ==================================================

    if windows is None:
        windows = []

    for window in windows:
        try:
            width = window.Width.Value
            opening_height = window.Height.Value
            sill_height = window.SillHeight.Value
            offset = window.Offset.Value

        except Exception:
            continue

        if width <= 0.001:
            continue

        if opening_height <= 0.001:
            continue

        if sill_height < 0.0:
            continue

        if offset < 0.0:
            continue

        if offset + width > length:
            continue

        if (
            sill_height
            + opening_height
            > height
        ):
            continue

        cutter_x = (
            start_extension
            + offset
        )

        cutter = Part.makeBox(
            width,
            cutter_depth,
            opening_height,
            App.Vector(
                cutter_x,
                cutter_y,
                sill_height,
            ),
        )

        try:
            shape = shape.cut(
                cutter
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD: błąd wycinania "
                f"okna {window.Label}: {error}\n"
            )

    # --------------------------------------------------
    # GLOBALNE POŁOŻENIE ŚCIANY
    # --------------------------------------------------

    shape.Placement = App.Placement(
        extended_start,
        App.Rotation(
            App.Vector(
                0.0,
                0.0,
                1.0,
            ),
            heading,
        ),
    )

    return shape


def get_room_for_wall(wall):
    """Find room containing a wall."""

    document = wall.Document

    if document is None:
        return None

    for obj in document.Objects:
        if (
            getattr(
                obj,
                "OICType",
                "",
            )
            != ROOM_TYPE
        ):
            continue

        try:
            if wall in obj.Group:
                return obj

        except Exception:
            continue

    return None


def get_room_walls(room):
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


def rebuild_room(room):
    """
    Rebuild complete parametric wall chain.

    Also updates the floor if the room already
    contains one.

    Dimensions are intentionally NOT rebuilt here.
    Their update remains handled by the existing
    dimension workflow to avoid references to
    already deleted dimension objects.
    """

    global _REBUILDING

    if room is None:
        return

    walls = get_room_walls(
        room
    )

    if not walls:
        return

    if _REBUILDING:
        return

    _REBUILDING = True

    try:
        first_wall = walls[0]
        previous_wall = None

        for wall in walls:
            proxy = getattr(
                wall,
                "Proxy",
                None,
            )

            if proxy is None:
                previous_wall = wall
                continue

            proxy.rebuild_geometry(
                wall,
                previous_wall=previous_wall,
                first_wall=first_wall,
            )

            previous_wall = wall

    finally:
        _REBUILDING = False

    # --------------------------------------------------
    # AUTOMATYCZNA AKTUALIZACJA PODŁOGI
    # --------------------------------------------------

    try:
        from OICFloor import rebuild_room_floor

        rebuild_room_floor(
            room
        )

    except ImportError:
        # OICFloor może jeszcze nie być załadowany.
        pass

    except Exception as error:
        App.Console.PrintError(
            "OpenInteriorCAD: nie udało się "
            "zaktualizować podłogi: "
            f"{error}\n"
        )

    # --------------------------------------------------
    # AKTUALIZACJA PODSTAWOWYCH OBLICZEŃ POMIESZCZENIA
    # --------------------------------------------------

    try:
        if "WallCount" in room.PropertiesList:
            room.WallCount = len(
                walls
            )

        if "Perimeter" in room.PropertiesList:
            room.Perimeter = sum(
                wall.Length.Value
                for wall in walls
            )

    except Exception as error:
        App.Console.PrintError(
            "OpenInteriorCAD: nie udało się "
            "zaktualizować danych pomieszczenia: "
            f"{error}\n"
        )

    # UWAGA:
    # Nie wywołujemy tutaj update_room_dimensions().
    #
    # Poprzednia wersja robiła to przy każdej
    # przebudowie ścian. OICDimensions usuwa stare
    # obiekty wymiarowe i podczas tej samej operacji
    # mogło dojść do:
    #
    # Cannot access attribute 'ViewObject'
    # of deleted object
    #
    # Wymiary naprawimy osobno.

    if room.Document is not None:
        try:
            room.Document.recompute()

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD: błąd recompute "
                f"pomieszczenia: {error}\n"
            )


def rebuild_from_wall(wall):
    """Rebuild wall and following room walls."""

    if wall is None:
        return

    room = get_room_for_wall(
        wall
    )

    if room is None:
        proxy = getattr(
            wall,
            "Proxy",
            None,
        )

        if proxy is not None:
            proxy.rebuild_geometry(
                wall
            )

        if wall.Document is not None:
            wall.Document.recompute()

        return

    rebuild_room(
        room
    )


class WallProxy:
    """Parametric OpenInteriorCAD wall."""

    TYPE_ID = WALL_TYPE

    def __init__(
        self,
        obj,
        start_point=None,
        length=4000.0,
        angle=0.0,
    ):
        self._add_properties(
            obj
        )

        obj.Proxy = self

        if start_point is None:
            start_point = App.Vector(
                0.0,
                0.0,
                0.0,
            )

        obj.StartPoint = start_point
        obj.Length = length
        obj.Angle = angle
        obj.Heading = angle

        obj.Thickness = 120.0
        obj.Height = 2600.0

        obj.ReferenceLine = REFERENCE_AXIS

        obj.ExtendStart = False
        obj.ExtendEnd = False

        obj.AutoClose = False

        self.rebuild_geometry(
            obj
        )

    def _add_properties(
        self,
        obj,
    ):
        """Create wall properties."""

        if "OICType" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyString",
                "OICType",
                "OpenInteriorCAD",
                "Semantic object type.",
            )

        if "StartPoint" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyVector",
                "StartPoint",
                "Geometria",
                "Punkt początkowy ściany.",
            )

            obj.setEditorMode(
                "StartPoint",
                1,
            )

        if "EndPoint" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyVector",
                "EndPoint",
                "Geometria",
                "Punkt końcowy ściany.",
            )

            obj.setEditorMode(
                "EndPoint",
                1,
            )

        if "Length" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Length",
                "Geometria",
                "Długość ściany.",
            )

        if "Angle" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyAngle",
                "Angle",
                "Geometria",
                (
                    "Pierwsza ściana: kąt względem osi X. "
                    "Pozostałe: kąt względem poprzedniej."
                ),
            )

        if "Heading" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyAngle",
                "Heading",
                "Geometria",
                "Wyliczony kierunek bezwzględny.",
            )

            obj.setEditorMode(
                "Heading",
                1,
            )

        if "Thickness" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Thickness",
                "Geometria",
                "Grubość ściany.",
            )

        if "Height" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "Geometria",
                "Wysokość ściany.",
            )

        if "ReferenceLine" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyEnumeration",
                "ReferenceLine",
                "Geometria",
                "Linia odniesienia ściany.",
            )

            obj.ReferenceLine = (
                REFERENCE_OPTIONS
            )

        if "ExtendStart" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyBool",
                "ExtendStart",
                "Narożniki",
                "Wydłuż początek bryły.",
            )

        if "ExtendEnd" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyBool",
                "ExtendEnd",
                "Narożniki",
                "Wydłuż koniec bryły.",
            )

        if "AutoClose" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyBool",
                "AutoClose",
                "OpenInteriorCAD",
                "Automatyczna ściana zamykająca.",
            )

            obj.setEditorMode(
                "AutoClose",
                1,
            )

        obj.OICType = self.TYPE_ID

    def rebuild_geometry(
        self,
        obj,
        previous_wall=None,
        first_wall=None,
    ):
        """Rebuild wall geometry."""

        if previous_wall is None:
            start_point = App.Vector(
                obj.StartPoint.x,
                obj.StartPoint.y,
                obj.StartPoint.z,
            )

            heading = obj.Angle.Value

        else:
            start_point = App.Vector(
                previous_wall.EndPoint.x,
                previous_wall.EndPoint.y,
                previous_wall.EndPoint.z,
            )

            heading = (
                previous_wall.Heading.Value
                + obj.Angle.Value
            )

        heading = normalize_angle(
            heading
        )

        # --------------------------------------------------
        # AUTOMATYCZNE ZAMKNIĘCIE OSTATNIEJ ŚCIANY
        # --------------------------------------------------

        if (
            obj.AutoClose
            and first_wall is not None
            and previous_wall is not None
        ):
            target_point = App.Vector(
                first_wall.StartPoint.x,
                first_wall.StartPoint.y,
                first_wall.StartPoint.z,
            )

            dx = (
                target_point.x
                - start_point.x
            )

            dy = (
                target_point.y
                - start_point.y
            )

            length = math.hypot(
                dx,
                dy,
            )

            if length > 0.001:
                heading = math.degrees(
                    math.atan2(
                        dy,
                        dx,
                    )
                )

                heading = normalize_angle(
                    heading
                )

                relative_angle = normalize_angle(
                    heading
                    - previous_wall.Heading.Value
                )

                obj.Angle = relative_angle
                obj.Length = length

            end_point = target_point

        else:
            length = obj.Length.Value

            angle_rad = math.radians(
                heading
            )

            end_point = App.Vector(
                start_point.x
                + length
                * math.cos(
                    angle_rad
                ),
                start_point.y
                + length
                * math.sin(
                    angle_rad
                ),
                start_point.z,
            )

        obj.StartPoint = start_point
        obj.EndPoint = end_point
        obj.Heading = heading

        # --------------------------------------------------
        # OTWORY W ŚCIANIE
        # --------------------------------------------------

        doors = get_wall_doors(
            obj
        )

        windows = get_wall_windows(
            obj
        )

        obj.Shape = build_wall_shape(
            start_point=start_point,
            heading=heading,
            length=obj.Length.Value,
            thickness=obj.Thickness.Value,
            height=obj.Height.Value,
            reference_line=str(
                obj.ReferenceLine
            ),
            extend_start=obj.ExtendStart,
            extend_end=obj.ExtendEnd,
            doors=doors,
            windows=windows,
        )


    def execute(
        self,
        obj,
    ):
        """FreeCAD recompute callback."""

        if _REBUILDING:
            return

        room = get_room_for_wall(
            obj
        )

        if room is None:
            self.rebuild_geometry(
                obj
            )

            return

        rebuild_room(
            room
        )


    def onChanged(
        self,
        obj,
        property_name,
    ):
        """React to wall changes."""

        if _REBUILDING:
            return

        if property_name not in {
            "Length",
            "Angle",
            "Thickness",
            "Height",
            "ReferenceLine",
            "ExtendStart",
            "ExtendEnd",
        }:
            return

        required = {
            "Length",
            "Angle",
            "Heading",
            "StartPoint",
            "EndPoint",
            "Thickness",
            "Height",
        }

        if not required.issubset(
            set(
                obj.PropertiesList
            )
        ):
            return

        rebuild_from_wall(
            obj
        )


    def onDocumentRestored(
        self,
        obj,
    ):
        """Restore wall after opening document."""

        self._add_properties(
            obj
        )

        obj.Proxy = self


class WallViewProvider:
    """View provider for OpenInteriorCAD walls."""

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


def create_wall(
    document,
    start_point=None,
    length=4000.0,
    angle=0.0,
    name="Wall",
):
    """Create a parametric OpenInteriorCAD wall."""

    obj = document.addObject(
        "Part::FeaturePython",
        name,
    )

    obj.Label = "Ściana"

    WallProxy(
        obj,
        start_point=start_point,
        length=length,
        angle=angle,
    )

    WallViewProvider(
        obj.ViewObject
    )

    document.recompute()

    obj.ViewObject.Visibility = True

    return obj