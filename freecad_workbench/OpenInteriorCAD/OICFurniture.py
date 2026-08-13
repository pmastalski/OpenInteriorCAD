"""Parametric furniture objects for OpenInteriorCAD."""

import FreeCAD as App
import Part


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"


class FurnitureProxy:
    """Parametric furniture box."""

    TYPE_ID = FURNITURE_TYPE

    def __init__(
        self,
        obj,
        width=600.0,
        depth=600.0,
        height=850.0,
        rotation=0.0,
        position=None,
    ):
        self._add_properties(
            obj
        )

        obj.Proxy = self

        if position is None:
            position = App.Vector(
                0.0,
                0.0,
                0.0,
            )

        obj.Width = width
        obj.Depth = depth
        obj.Height = height
        obj.RotationAngle = rotation
        obj.Position = position

        self.rebuild_geometry(
            obj
        )

    def _add_properties(
        self,
        obj,
    ):
        """Create furniture properties."""

        if "OICType" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyString",
                "OICType",
                "OpenInteriorCAD",
                "Semantic object type.",
            )

        if "Width" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Width",
                "Wymiary",
                "Szerokość mebla.",
            )

        if "Depth" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Depth",
                "Wymiary",
                "Głębokość mebla.",
            )

        if "Height" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "Wymiary",
                "Wysokość mebla.",
            )

        if "Position" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyVector",
                "Position",
                "Położenie",
                "Położenie mebla.",
            )

        if "RotationAngle" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyAngle",
                "RotationAngle",
                "Położenie",
                "Obrót mebla wokół osi Z.",
            )

        obj.OICType = self.TYPE_ID

    def rebuild_geometry(
        self,
        obj,
    ):
        """Rebuild furniture solid."""

        width = obj.Width.Value
        depth = obj.Depth.Value
        height = obj.Height.Value

        if width <= 0.001:
            obj.Shape = Part.Shape()
            return

        if depth <= 0.001:
            obj.Shape = Part.Shape()
            return

        if height <= 0.001:
            obj.Shape = Part.Shape()
            return

        shape = Part.makeBox(
            width,
            depth,
            height,
        )

        shape.Placement = App.Placement(
            App.Vector(
                obj.Position.x,
                obj.Position.y,
                obj.Position.z,
            ),
            App.Rotation(
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                obj.RotationAngle.Value,
            ),
        )

        obj.Shape = shape

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
            "Width",
            "Depth",
            "Height",
            "Position",
            "RotationAngle",
        }:
            return

        required = {
            "Width",
            "Depth",
            "Height",
            "Position",
            "RotationAngle",
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
                "OpenInteriorCAD furniture update error: "
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


class FurnitureViewProvider:
    """View provider for OpenInteriorCAD furniture."""

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


def create_furniture(
    document,
    position,
    width=600.0,
    depth=600.0,
    height=850.0,
    rotation=0.0,
    name="Furniture",
):
    """Create one parametric furniture object."""

    obj = document.addObject(
        "Part::FeaturePython",
        name,
    )

    obj.Label = "Cabinet"

    FurnitureProxy(
        obj,
        width=width,
        depth=depth,
        height=height,
        rotation=rotation,
        position=position,
    )

    FurnitureViewProvider(
        obj.ViewObject
    )

    document.recompute()

    try:
        obj.ViewObject.ShapeColor = (
            0.78,
            0.68,
            0.52,
        )

    except Exception:
        pass

    obj.ViewObject.Visibility = True

    return obj