"""Furniture duplication helpers for OpenInteriorCAD."""

import math

import FreeCAD as App


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"


def furniture_x_axis(
    furniture,
):
    """Return local +X direction of furniture."""

    angle = math.radians(
        furniture.RotationAngle.Value
    )

    return App.Vector(
        math.cos(angle),
        math.sin(angle),
        0.0,
    )


def duplicate_furniture(
    furniture,
    side="right",
):
    """
    Duplicate furniture directly beside source.

    side:
        "left"
        "right"
    """

    document = furniture.Document

    if document is None:
        return None

    x_axis = furniture_x_axis(
        furniture
    )

    source_position = furniture.Position

    source_width = furniture.Width.Value
    source_depth = furniture.Depth.Value
    source_height = furniture.Height.Value

    rotation = furniture.RotationAngle.Value

    # ----------------------------------------------
    # POSITION
    # ----------------------------------------------

    if side == "left":
        new_position = App.Vector(
            source_position.x
            - x_axis.x * source_width,
            source_position.y
            - x_axis.y * source_width,
            source_position.z,
        )

    else:
        new_position = App.Vector(
            source_position.x
            + x_axis.x * source_width,
            source_position.y
            + x_axis.y * source_width,
            source_position.z,
        )

    # ----------------------------------------------
    # CREATE
    # ----------------------------------------------

    from OICFurniture import create_furniture

    new_furniture = create_furniture(
        document=document,
        position=new_position,
        width=source_width,
        depth=source_depth,
        height=source_height,
        rotation=rotation,
    )

    new_furniture.Label = (
        furniture.Label
    )

    document.recompute()

    return new_furniture