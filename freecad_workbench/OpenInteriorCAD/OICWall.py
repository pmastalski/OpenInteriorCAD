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


def build_wall_shape(
    start_point,
    end_point,
    thickness,
    height,
    reference_line,
):
    """Build a wall solid between two points in the XY plane."""

    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y

    length = math.hypot(
        dx,
        dy,
    )

    if length <= 0.001:
        return Part.Shape()

    if thickness <= 0.001:
        return Part.Shape()

    if height <= 0.001:
        return Part.Shape()

    # Lokalnie ściana jest zawsze budowana
    # wzdłuż dodatniej osi X.
    #
    # Oś Y określa, po której stronie linii
    # referencyjnej znajduje się grubość ściany.

    if reference_line == REFERENCE_LEFT:
        y_offset = 0.0

    elif reference_line == REFERENCE_RIGHT:
        y_offset = -thickness

    else:
        # Domyślnie ściana jest centrowana
        # względem osi rysowania.
        y_offset = -thickness / 2.0

    shape = Part.makeBox(
        length,
        thickness,
        height,
        App.Vector(
            0.0,
            y_offset,
            0.0,
        ),
    )

    angle = math.degrees(
        math.atan2(
            dy,
            dx,
        )
    )

    placement = App.Placement(
        App.Vector(
            start_point.x,
            start_point.y,
            start_point.z,
        ),
        App.Rotation(
            App.Vector(
                0.0,
                0.0,
                1.0,
            ),
            angle,
        ),
    )

    shape.Placement = placement

    return shape


class WallProxy:
    """Parametric OpenInteriorCAD wall."""

    TYPE_ID = "OpenInteriorCAD::Wall"

    def __init__(
        self,
        obj,
        start_point=None,
        end_point=None,
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

        if end_point is None:
            end_point = App.Vector(
                4000.0,
                0.0,
                0.0,
            )

        obj.StartPoint = start_point
        obj.EndPoint = end_point

        obj.Thickness = 120.0
        obj.Height = 2600.0

        obj.ReferenceLine = REFERENCE_AXIS

    def _add_properties(
        self,
        obj,
    ):
        """Create all OpenInteriorCAD wall properties."""

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
                "Punkt początkowy osi ściany.",
            )

        if "EndPoint" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyVector",
                "EndPoint",
                "Geometria",
                "Punkt końcowy osi ściany.",
            )

        if "Length" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Length",
                "Geometria",
                "Obliczona długość ściany.",
            )

            obj.setEditorMode(
                "Length",
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
                "Sposób odkładania grubości względem osi rysowania.",
            )

            obj.ReferenceLine = REFERENCE_OPTIONS

        obj.OICType = self.TYPE_ID

    def execute(
        self,
        obj,
    ):
        """Regenerate wall geometry."""

        start_point = obj.StartPoint
        end_point = obj.EndPoint

        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y

        length = math.hypot(
            dx,
            dy,
        )

        obj.Length = length

        shape = build_wall_shape(
            start_point=start_point,
            end_point=end_point,
            thickness=obj.Thickness.Value,
            height=obj.Height.Value,
            reference_line=str(
                obj.ReferenceLine
            ),
        )

        obj.Shape = shape

    def onChanged(
        self,
        obj,
        property_name,
    ):
        """React to editable property changes."""

        if property_name not in {
            "StartPoint",
            "EndPoint",
            "Thickness",
            "Height",
            "ReferenceLine",
        }:
            return

        required_properties = {
            "StartPoint",
            "EndPoint",
            "Thickness",
            "Height",
            "Length",
            "ReferenceLine",
        }

        if not required_properties.issubset(
            set(
                obj.PropertiesList
            )
        ):
            return

        try:
            self.execute(
                obj
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD wall update error: "
                f"{error}\n"
            )

    def onDocumentRestored(
        self,
        obj,
    ):
        """Restore proxy after opening a FreeCAD document."""

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
    end_point=None,
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
        end_point=end_point,
    )

    WallViewProvider(
        obj.ViewObject
    )

    document.recompute()

    obj.ViewObject.Visibility = True

    return obj