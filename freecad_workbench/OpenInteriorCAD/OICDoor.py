"""Parametric OpenInteriorCAD door object."""

import math

import FreeCAD as App
import Part
from pivy import coin


DOOR_TYPE = "OpenInteriorCAD::Door"

SWING_LEFT = "Lewy"
SWING_RIGHT = "Prawy"

DIRECTION_IN = "Do wewnątrz"
DIRECTION_OUT = "Na zewnątrz"


def rebuild_host_wall(door):
    """Rebuild host wall after door parameter changes."""

    wall = getattr(
        door,
        "HostWall",
        None,
    )

    if wall is None:
        return

    try:
        from OICWall import rebuild_from_wall

        rebuild_from_wall(
            wall
        )

    except Exception as error:
        App.Console.PrintError(
            "OpenInteriorCAD: nie udało się "
            "przebudować ściany po zmianie drzwi: "
            f"{error}\n"
        )


class DoorProxy:
    """Parametric door opening attached to a wall."""

    TYPE_ID = DOOR_TYPE

    def __init__(
        self,
        obj,
        wall=None,
        width=900.0,
        height=2100.0,
        offset=500.0,
    ):
        self._add_properties(
            obj
        )

        obj.Proxy = self

        if wall is not None:
            obj.HostWall = wall

        obj.Width = width
        obj.Height = height
        obj.Offset = offset

        obj.SwingSide = [
            SWING_LEFT,
            SWING_RIGHT,
        ]
        obj.SwingSide = SWING_LEFT

        obj.SwingDirection = [
            DIRECTION_IN,
            DIRECTION_OUT,
        ]
        obj.SwingDirection = DIRECTION_IN

        self.rebuild_geometry(
            obj
        )

    def _add_properties(
        self,
        obj,
    ):
        """Create door properties."""

        if "OICType" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyString",
                "OICType",
                "OpenInteriorCAD",
                "Semantic object type.",
            )

        if "HostWall" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLink",
                "HostWall",
                "Drzwi",
                "Ściana, w której znajdują się drzwi.",
            )

        if "Width" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Width",
                "Drzwi",
                "Szerokość otworu drzwiowego.",
            )

        if "Height" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "Drzwi",
                "Wysokość otworu drzwiowego.",
            )

        if "Offset" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Offset",
                "Drzwi",
                "Odległość od początku ściany.",
            )

        if "SwingSide" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyEnumeration",
                "SwingSide",
                "Drzwi",
                "Strona zawiasów.",
            )

            obj.SwingSide = [
                SWING_LEFT,
                SWING_RIGHT,
            ]

        if "SwingDirection" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyEnumeration",
                "SwingDirection",
                "Drzwi",
                "Kierunek otwierania.",
            )

            obj.SwingDirection = [
                DIRECTION_IN,
                DIRECTION_OUT,
            ]

        obj.OICType = self.TYPE_ID

    def _validate_parameters(
        self,
        obj,
    ):
        """Keep door parameters inside wall limits."""

        wall = obj.HostWall

        if wall is None:
            return

        wall_length = wall.Length.Value

        if obj.Width.Value >= wall_length:
            obj.Width = max(
                1.0,
                wall_length - 1.0,
            )

        if obj.Offset.Value < 0.0:
            obj.Offset = 0.0

        maximum_offset = max(
            0.0,
            wall_length
            - obj.Width.Value,
        )

        if obj.Offset.Value > maximum_offset:
            obj.Offset = maximum_offset

        if obj.Height.Value > wall.Height.Value:
            obj.Height = wall.Height.Value

    def rebuild_geometry(
        self,
        obj,
    ):
        """
        Update the door placement.

        Door geometry is not responsible for cutting
        the opening. OICWall performs the Boolean cut.
        """

        wall = obj.HostWall

        if wall is None:
            obj.Shape = Part.Shape()
            return

        self._validate_parameters(
            obj
        )

        heading = wall.Heading.Value
        heading_rad = math.radians(
            heading
        )

        ux = math.cos(
            heading_rad
        )

        uy = math.sin(
            heading_rad
        )

        wall_start = wall.StartPoint

        door_position = App.Vector(
            wall_start.x
            + ux * obj.Offset.Value,
            wall_start.y
            + uy * obj.Offset.Value,
            wall_start.z,
        )

        # IMPORTANT:
        #
        # Placement now belongs to the Door object itself.
        # The ViewProvider will use LOCAL coordinates.
        obj.Placement = App.Placement(
            door_position,
            App.Rotation(
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                heading,
            ),
        )

        # The visible representation is handled entirely
        # by DoorViewProvider.
        obj.Shape = Part.Shape()

    def execute(
        self,
        obj,
    ):
        """FreeCAD recompute callback."""

        self.rebuild_geometry(
            obj
        )

    def onChanged(
        self,
        obj,
        property_name,
    ):
        """React to door property changes."""

        if property_name not in {
            "HostWall",
            "Width",
            "Height",
            "Offset",
            "SwingSide",
            "SwingDirection",
        }:
            return

        required = {
            "HostWall",
            "Width",
            "Height",
            "Offset",
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

            rebuild_host_wall(
                obj
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD door update error: "
                f"{error}\n"
            )

    def onDocumentRestored(
        self,
        obj,
    ):
        """Restore door after document loading."""

        self._add_properties(
            obj
        )

        obj.Proxy = self


class DoorViewProvider:
    """2D architectural door symbol."""

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
        """Create the local door symbol."""

        try:
            self.root = coin.SoSeparator()

            view_object.addDisplayMode(
                self.root,
                "DoorSymbol",
            )

            self._rebuild_symbol(
                view_object.Object
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD door symbol error: "
                f"{error}\n"
            )

    def _add_line(
        self,
        parent,
        point1,
        point2,
    ):
        """Add one line in local door coordinates."""

        separator = coin.SoSeparator()

        coords = coin.SoCoordinate3()

        coords.point.setValues(
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
            coords
        )

        separator.addChild(
            line
        )

        parent.addChild(
            separator
        )

    def _rebuild_symbol(
        self,
        door,
    ):
        """
        Build door symbol in LOCAL coordinates.

        X = along wall
        Y = perpendicular to wall
        """

        if self.root is None:
            return

        self.root.removeAllChildren()

        wall = door.HostWall

        if wall is None:
            return

        width = door.Width.Value

        if width <= 0.001:
            return

        color = coin.SoBaseColor()

        color.rgb = (
            1.0,
            1.0,
            1.0,
        )

        style = coin.SoDrawStyle()

        style.lineWidth = 2.0

        self.root.addChild(
            color
        )

        self.root.addChild(
            style
        )

        z = 150.0

        # --------------------------------------------------
        # Which side of wall?
        # --------------------------------------------------

        side = 1.0

        if (
            str(
                door.SwingDirection
            )
            == DIRECTION_OUT
        ):
            side = -1.0

        half_thickness = (
            wall.Thickness.Value
            / 2.0
        )

        wall_edge_y = (
            side
            * half_thickness
        )

        # --------------------------------------------------
        # Hinges
        # --------------------------------------------------

        if (
            str(
                door.SwingSide
            )
            == SWING_LEFT
        ):
            hinge_x = 0.0
            closed_x = width

            arc_sign = 1.0

        else:
            hinge_x = width
            closed_x = 0.0

            arc_sign = -1.0

        hinge = App.Vector(
            hinge_x,
            wall_edge_y,
            z,
        )

        closed_end = App.Vector(
            closed_x,
            wall_edge_y,
            z,
        )

        open_end = App.Vector(
            hinge_x,
            wall_edge_y
            + side * width,
            z,
        )

        # --------------------------------------------------
        # Closed leaf line
        # --------------------------------------------------

        self._add_line(
            self.root,
            hinge,
            closed_end,
        )

        # --------------------------------------------------
        # Open leaf line
        # --------------------------------------------------

        self._add_line(
            self.root,
            hinge,
            open_end,
        )

        # --------------------------------------------------
        # Swing arc
        # --------------------------------------------------

        points = []

        steps = 24

        for index in range(
            steps + 1
        ):
            angle = (
                math.pi / 2.0
                * index
                / steps
            )

            x = (
                hinge_x
                + arc_sign
                * width
                * math.cos(
                    angle
                )
            )

            y = (
                wall_edge_y
                + side
                * width
                * math.sin(
                    angle
                )
            )

            points.append(
                App.Vector(
                    x,
                    y,
                    z,
                )
            )

        for index in range(
            len(points) - 1
        ):
            self._add_line(
                self.root,
                points[index],
                points[index + 1],
            )

    def updateData(
        self,
        obj,
        property_name,
    ):
        """Update symbol after door changes."""

        if property_name in {
            "HostWall",
            "Width",
            "Offset",
            "SwingSide",
            "SwingDirection",
        }:
            self._rebuild_symbol(
                obj
            )

    def getDisplayModes(
        self,
        view_object,
    ):
        return [
            "DoorSymbol",
        ]

    def getDefaultDisplayMode(
        self,
    ):
        return "DoorSymbol"

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


def create_door(
    document,
    wall,
    width=900.0,
    height=2100.0,
    offset=500.0,
    name="Door",
):
    """Create a parametric OpenInteriorCAD door."""

    obj = document.addObject(
        "Part::FeaturePython",
        name,
    )

    obj.Label = "Door"

    DoorProxy(
        obj,
        wall=wall,
        width=width,
        height=height,
        offset=offset,
    )

    DoorViewProvider(
        obj.ViewObject
    )

    document.recompute()

    try:
        obj.ViewObject.DisplayMode = (
            "DoorSymbol"
        )
    except Exception:
        pass

    obj.ViewObject.Visibility = True

    rebuild_host_wall(
        obj
    )

    document.recompute()

    return obj