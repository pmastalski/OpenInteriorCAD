"""Standalone board / filler element for OpenInteriorCAD 0.8.

The object is intentionally simple:
- one rectangular board,
- editable dimensions and placement,
- selectable edge-banding sides,
- production metadata compatible with Cut List / Cut Layout.

Local geometry:
- X = Width
- Y = Thickness
- Z = Height

This default orientation makes a newly inserted filler a vertical panel.
"""

from __future__ import annotations

import FreeCAD as App
import Part


OIC_TYPE = "OpenInteriorCAD::BoardElement"


class BoardElementProxy:
    def __init__(self, obj):
        self.Object = obj
        obj.Proxy = self
        self._add_properties(obj)
        self.execute(obj)

    def _add_properties(self, obj):
        def add(prop_type, name, group, description):
            if name not in obj.PropertiesList:
                obj.addProperty(prop_type, name, group, description)

        add(
            "App::PropertyString",
            "OICType",
            "OpenInteriorCAD",
            "OpenInteriorCAD object type.",
        )
        obj.OICType = OIC_TYPE
        obj.setEditorMode("OICType", 1)

        add(
            "App::PropertyLength",
            "Width",
            "Dimensions",
            "Panel width along local X.",
        )
        add(
            "App::PropertyLength",
            "Height",
            "Dimensions",
            "Panel height along local Z.",
        )
        add(
            "App::PropertyLength",
            "Thickness",
            "Dimensions",
            "Panel thickness along local Y.",
        )

        if obj.Width.Value <= 0:
            obj.Width = 100.0
        if obj.Height.Value <= 0:
            obj.Height = 720.0
        if obj.Thickness.Value <= 0:
            obj.Thickness = 18.0

        add(
            "App::PropertyString",
            "BoardMaterial",
            "Production",
            "Board material used in production lists.",
        )
        add(
            "App::PropertyString",
            "EdgeMaterial",
            "Production",
            "Edge-band material.",
        )
        add(
            "App::PropertyLength",
            "EdgeThickness",
            "Production",
            "Edge-band thickness.",
        )

        if not str(obj.BoardMaterial).strip():
            obj.BoardMaterial = "Carcass Board"
        if not str(obj.EdgeMaterial).strip():
            obj.EdgeMaterial = "ABS"
        if obj.EdgeThickness.Value <= 0:
            obj.EdgeThickness = 0.8

        # Edge naming follows what the user sees when looking at the large
        # face of the filler: Top / Bottom / Left / Right.
        add(
            "App::PropertyBool",
            "EdgeTop",
            "Edge Banding",
            "Apply edge banding to the top edge.",
        )
        add(
            "App::PropertyBool",
            "EdgeBottom",
            "Edge Banding",
            "Apply edge banding to the bottom edge.",
        )
        add(
            "App::PropertyBool",
            "EdgeLeft",
            "Edge Banding",
            "Apply edge banding to the left edge.",
        )
        add(
            "App::PropertyBool",
            "EdgeRight",
            "Edge Banding",
            "Apply edge banding to the right edge.",
        )

        # Useful installation metadata.
        add(
            "App::PropertyString",
            "ElementRole",
            "OpenInteriorCAD",
            "Logical element role.",
        )
        if not str(obj.ElementRole).strip():
            obj.ElementRole = "Filler"

    def execute(self, obj):
        width = max(0.001, float(obj.Width.Value))
        height = max(0.001, float(obj.Height.Value))
        thickness = max(0.001, float(obj.Thickness.Value))

        obj.Shape = Part.makeBox(
            width,
            thickness,
            height,
        )

    def onChanged(self, obj, prop):
        if prop in {
            "Width",
            "Height",
            "Thickness",
        }:
            try:
                self.execute(obj)
            except Exception as error:
                App.Console.PrintError(
                    f"OpenInteriorCAD filler rebuild error: {error}\n"
                )

    def onDocumentRestored(self, obj):
        self.Object = obj
        self._add_properties(obj)


def create_filler(
    document=None,
    name="Filler",
    width=100.0,
    height=720.0,
    thickness=18.0,
):
    if document is None:
        document = App.ActiveDocument

    if document is None:
        document = App.newDocument("OpenInteriorCAD")

    # Standalone fillers must be regular Part FeaturePython objects.
    # PartDesign::FeaturePython expects to live inside an active Body and can
    # otherwise appear with a crossed-out visibility icon and an unusable
    # ViewObject in the tree.
    obj = document.addObject(
        "Part::FeaturePython",
        "OICFiller",
    )
    obj.Label = name

    BoardElementProxy(obj)

    obj.Width = width
    obj.Height = height
    obj.Thickness = thickness

    document.recompute()

    try:
        obj.ViewObject.Visibility = True
    except Exception:
        pass

    return obj
