"""Parametric wall object for OpenInteriorCAD."""

import Part


class WallProxy:
    """FreeCAD FeaturePython proxy representing an interior wall."""

    TYPE_ID = "OpenInteriorCAD::Wall"

    def __init__(self, obj):
        self._add_properties(obj)

        obj.Proxy = self

        obj.Length = 4000.0
        obj.Thickness = 120.0
        obj.Height = 2600.0

    def _add_properties(self, obj):
        if "OICType" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyString",
                "OICType",
                "OpenInteriorCAD",
                "Semantic OpenInteriorCAD object type.",
            )

        if "Length" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Length",
                "Geometry",
                "Wall length.",
            )

        if "Thickness" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Thickness",
                "Geometry",
                "Wall thickness.",
            )

        if "Height" not in obj.PropertiesList:
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "Geometry",
                "Wall height.",
            )

        obj.OICType = self.TYPE_ID

    def execute(self, obj):
        length = obj.Length.Value
        thickness = obj.Thickness.Value
        height = obj.Height.Value

        if length <= 0:
            obj.Shape = Part.Shape()
            return

        if thickness <= 0:
            obj.Shape = Part.Shape()
            return

        if height <= 0:
            obj.Shape = Part.Shape()
            return

        obj.Shape = Part.makeBox(
            length,
            thickness,
            height,
        )

    def onDocumentRestored(self, obj):
        self._add_properties(obj)

        obj.Proxy = self


def create_wall(
    document,
    name="Wall",
):
    """Create a new parametric OpenInteriorCAD wall."""

    obj = document.addObject(
        "PartDesign::FeaturePython",
        name,
    )

    obj.Label = "Ściana"

    WallProxy(
        obj
    )

    document.recompute()

    return obj