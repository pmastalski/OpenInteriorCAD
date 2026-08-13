"""Stable CAD-style dimensions for OpenInteriorCAD."""

import math

import FreeCAD as App
from pivy import coin


DIMENSION_TYPE = "OpenInteriorCAD::Dimension"
DIMENSION_GROUP_TYPE = "OpenInteriorCAD::DimensionGroup"
WALL_TYPE = "OpenInteriorCAD::Wall"

DIMENSION_OFFSET = 120.0
EXTENSION_OVERHANG = 45.0

ARROW_LENGTH = 80.0
ARROW_HALF_WIDTH = 30.0

TEXT_OFFSET = 45.0

Z_LEVEL = 120.0


def get_room_walls(room):
    """Return room walls in drawing order."""

    return [
        obj
        for obj in room.Group
        if getattr(obj, "OICType", "") == WALL_TYPE
    ]


def get_dimensions_group(
    room,
    create=True,
):
    """Return or create dimensions group."""

    document = room.Document

    if document is None:
        return None

    for obj in room.Group:
        if (
            getattr(obj, "OICType", "")
            == DIMENSION_GROUP_TYPE
        ):
            return obj

    if not create:
        return None

    group = document.addObject(
        "App::DocumentObjectGroup",
        "Dimensions",
    )

    group.Label = "Wymiary"

    if "OICType" not in group.PropertiesList:
        group.addProperty(
            "App::PropertyString",
            "OICType",
            "OpenInteriorCAD",
            "Semantic object type.",
        )

    group.OICType = DIMENSION_GROUP_TYPE

    room.addObject(group)

    group.ViewObject.Visibility = True

    return group


def clear_room_dimensions(room):
    """Delete all generated dimensions."""

    document = room.Document

    if document is None:
        return

    group = get_dimensions_group(
        room,
        create=False,
    )

    if group is None:
        return

    for dimension in list(group.Group):
        try:
            group.removeObject(dimension)
        except Exception:
            pass

        try:
            document.removeObject(
                dimension.Name
            )
        except Exception:
            pass


def _room_orientation(walls):
    """Calculate signed polygon area."""

    if len(walls) < 3:
        return 0.0

    area = 0.0

    points = [
        wall.StartPoint
        for wall in walls
    ]

    for index, point in enumerate(points):
        next_point = points[
            (index + 1) % len(points)
        ]

        area += (
            point.x * next_point.y
            - next_point.x * point.y
        )

    return area / 2.0


def _wall_direction(wall):
    """Return unit wall direction and wall length."""

    dx = (
        wall.EndPoint.x
        - wall.StartPoint.x
    )

    dy = (
        wall.EndPoint.y
        - wall.StartPoint.y
    )

    length = math.hypot(
        dx,
        dy,
    )

    if length <= 0.001:
        return (
            App.Vector(
                1.0,
                0.0,
                0.0,
            ),
            0.0,
        )

    return (
        App.Vector(
            dx / length,
            dy / length,
            0.0,
        ),
        length,
    )


def _outside_normal(
    wall,
    orientation,
):
    """Return normal pointing outside the room."""

    direction, length = _wall_direction(
        wall
    )

    if length <= 0.001:
        return App.Vector(
            0.0,
            1.0,
            0.0,
        )

    left = App.Vector(
        -direction.y,
        direction.x,
        0.0,
    )

    right = App.Vector(
        direction.y,
        -direction.x,
        0.0,
    )

    if orientation > 0:
        return right

    if orientation < 0:
        return left

    return left


class DimensionProxy:
    """OpenInteriorCAD dimension data."""

    def __init__(
        self,
        obj,
        wall,
        orientation,
    ):
        if "OICType" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyString",
                "OICType",
                "OpenInteriorCAD",
            )

        if "SourceWall" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLink",
                "SourceWall",
                "OpenInteriorCAD",
            )

        if "RoomOrientation" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyFloat",
                "RoomOrientation",
                "OpenInteriorCAD",
            )

        obj.OICType = DIMENSION_TYPE
        obj.SourceWall = wall
        obj.RoomOrientation = orientation

        obj.Proxy = self

    def execute(
        self,
        obj,
    ):
        pass


class DimensionViewProvider:
    """Visible CAD-style dimension ViewProvider."""

    def __init__(
        self,
        view_object,
    ):
        self.root = None

        view_object.Proxy = self

    def attach(
        self,
        view_object,
    ):
        """Build dimension scene."""

        try:
            obj = view_object.Object

            wall = obj.SourceWall

            if wall is None:
                return

            self.root = coin.SoSeparator()

            self._build_dimension(
                self.root,
                wall,
                obj.RoomOrientation,
            )

            view_object.addDisplayMode(
                self.root,
                "Dimension",
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD dimension attach error: "
                f"{error}\n"
            )

    def _add_line(
        self,
        parent,
        point1,
        point2,
    ):
        """Add one simple visible line."""

        separator = coin.SoSeparator()

        coordinates = coin.SoCoordinate3()

        coordinates.point.setValues(
            0,
            2,
            [
                (
                    point1.x,
                    point1.y,
                    point1.z,
                ),
                (
                    point2.x,
                    point2.y,
                    point2.z,
                ),
            ],
        )

        line = coin.SoLineSet()

        line.numVertices.setValue(
            2
        )

        separator.addChild(
            coordinates
        )

        separator.addChild(
            line
        )

        parent.addChild(
            separator
        )

    def _build_dimension(
        self,
        root,
        wall,
        orientation,
    ):
        """Build complete dimension."""

        # Jasny kolor pod ciemny motyw FreeCADa.
        line_color = coin.SoBaseColor()

        line_color.rgb = (
            0.90,
            0.90,
            0.90,
        )

        line_style = coin.SoDrawStyle()

        line_style.lineWidth = 2.5

        root.addChild(
            line_color
        )

        root.addChild(
            line_style
        )

        start = App.Vector(
            wall.StartPoint.x,
            wall.StartPoint.y,
            Z_LEVEL,
        )

        end = App.Vector(
            wall.EndPoint.x,
            wall.EndPoint.y,
            Z_LEVEL,
        )

        direction, length = _wall_direction(
            wall
        )

        if length <= 0.001:
            return

        normal = _outside_normal(
            wall,
            orientation,
        )

        offset = (
            wall.Thickness.Value / 2.0
            + DIMENSION_OFFSET
        )

        dim_start = App.Vector(
            start.x
            + normal.x * offset,
            start.y
            + normal.y * offset,
            Z_LEVEL,
        )

        dim_end = App.Vector(
            end.x
            + normal.x * offset,
            end.y
            + normal.y * offset,
            Z_LEVEL,
        )

        extension_start_end = App.Vector(
            dim_start.x
            + normal.x
            * EXTENSION_OVERHANG,
            dim_start.y
            + normal.y
            * EXTENSION_OVERHANG,
            Z_LEVEL,
        )

        extension_end_end = App.Vector(
            dim_end.x
            + normal.x
            * EXTENSION_OVERHANG,
            dim_end.y
            + normal.y
            * EXTENSION_OVERHANG,
            Z_LEVEL,
        )

        # Linie pomocnicze.
        self._add_line(
            root,
            start,
            extension_start_end,
        )

        self._add_line(
            root,
            end,
            extension_end_end,
        )

        # Główna linia wymiarowa.
        self._add_line(
            root,
            dim_start,
            dim_end,
        )

        # Grot początkowy.
        arrow_start_1 = App.Vector(
            dim_start.x
            + direction.x
            * ARROW_LENGTH
            + normal.x
            * ARROW_HALF_WIDTH,
            dim_start.y
            + direction.y
            * ARROW_LENGTH
            + normal.y
            * ARROW_HALF_WIDTH,
            Z_LEVEL,
        )

        arrow_start_2 = App.Vector(
            dim_start.x
            + direction.x
            * ARROW_LENGTH
            - normal.x
            * ARROW_HALF_WIDTH,
            dim_start.y
            + direction.y
            * ARROW_LENGTH
            - normal.y
            * ARROW_HALF_WIDTH,
            Z_LEVEL,
        )

        self._add_line(
            root,
            dim_start,
            arrow_start_1,
        )

        self._add_line(
            root,
            dim_start,
            arrow_start_2,
        )

        # Grot końcowy.
        arrow_end_1 = App.Vector(
            dim_end.x
            - direction.x
            * ARROW_LENGTH
            + normal.x
            * ARROW_HALF_WIDTH,
            dim_end.y
            - direction.y
            * ARROW_LENGTH
            + normal.y
            * ARROW_HALF_WIDTH,
            Z_LEVEL,
        )

        arrow_end_2 = App.Vector(
            dim_end.x
            - direction.x
            * ARROW_LENGTH
            - normal.x
            * ARROW_HALF_WIDTH,
            dim_end.y
            - direction.y
            * ARROW_LENGTH
            - normal.y
            * ARROW_HALF_WIDTH,
            Z_LEVEL,
        )

        self._add_line(
            root,
            dim_end,
            arrow_end_1,
        )

        self._add_line(
            root,
            dim_end,
            arrow_end_2,
        )

        # Tekst.
        midpoint = App.Vector(
            (
                dim_start.x
                + dim_end.x
            )
            / 2.0,
            (
                dim_start.y
                + dim_end.y
            )
            / 2.0,
            Z_LEVEL,
        )

        text_position = App.Vector(
            midpoint.x
            + normal.x * TEXT_OFFSET,
            midpoint.y
            + normal.y * TEXT_OFFSET,
            Z_LEVEL + 20.0,
        )

        text_separator = coin.SoSeparator()

        text_color = coin.SoBaseColor()

        text_color.rgb = (
            1.0,
            1.0,
            1.0,
        )

        font = coin.SoFont()

        font.size = 20

        translation = coin.SoTranslation()

        translation.translation.setValue(
            text_position.x,
            text_position.y,
            text_position.z,
        )

        text = coin.SoText2()

        text.justification = (
            coin.SoText2.CENTER
        )

        text.string.setValue(
            f"{wall.Length.Value:.0f}"
        )

        text_separator.addChild(
            text_color
        )

        text_separator.addChild(
            font
        )

        text_separator.addChild(
            translation
        )

        text_separator.addChild(
            text
        )

        root.addChild(
            text_separator
        )

    def getDisplayModes(
        self,
        view_object,
    ):
        return [
            "Dimension",
        ]

    def getDefaultDisplayMode(
        self,
    ):
        return "Dimension"

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
        pass

    def updateData(
        self,
        obj,
        property_name,
    ):
        pass

    def dumps(
        self,
    ):
        return None

    def loads(
        self,
        state,
    ):
        return None


def create_dimension(
    room,
    wall,
    orientation,
):
    """Create one OpenInteriorCAD dimension."""

    document = room.Document

    dimension = document.addObject(
        "App::FeaturePython",
        "WallDimension",
    )

    dimension.Label = (
        f"Wymiar {wall.Label}"
    )

    DimensionProxy(
        dimension,
        wall,
        orientation,
    )

    DimensionViewProvider(
        dimension.ViewObject
    )

    document.recompute()

    try:
        dimension.ViewObject.DisplayMode = (
            "Dimension"
        )
    except Exception as error:
        App.Console.PrintWarning(
            "OpenInteriorCAD DisplayMode warning: "
            f"{error}\n"
        )

    dimension.ViewObject.Visibility = True

    return dimension


def update_room_dimensions(room):
    """Recreate dimensions for all room walls."""

    if room is None:
        return

    document = room.Document

    if document is None:
        return

    walls = get_room_walls(
        room
    )

    if not walls:
        return

    clear_room_dimensions(
        room
    )

    group = get_dimensions_group(
        room,
        create=True,
    )

    orientation = _room_orientation(
        walls
    )

    dimensions = []

    for wall in walls:
        dimension = create_dimension(
            room,
            wall,
            orientation,
        )

        group.addObject(
            dimension
        )

        dimensions.append(
            dimension
        )

    document.recompute()

    group.ViewObject.Visibility = True

    for dimension in dimensions:
        dimension.ViewObject.Visibility = True

        try:
            dimension.ViewObject.DisplayMode = (
                "Dimension"
            )
        except Exception:
            pass

    document.recompute()

    App.Console.PrintMessage(
        "OpenInteriorCAD: "
        f"utworzono {len(dimensions)} wymiarów.\n"
    )