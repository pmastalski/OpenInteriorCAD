"""Furniture duplication helpers for OpenInteriorCAD."""

import math
import FreeCAD as App


def furniture_x_axis(
    furniture,
):
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
    """Duplicate Cabinet and preserve standard/corner/blind configuration."""

    document = furniture.Document

    if document is None:
        return None

    x_axis = furniture_x_axis(
        furniture
    )

    direction = (
        -1.0
        if side == "left"
        else 1.0
    )

    new_position = App.Vector(
        furniture.Position.x
        + x_axis.x
        * furniture.Width.Value
        * direction,
        furniture.Position.y
        + x_axis.y
        * furniture.Width.Value
        * direction,
        furniture.Position.z,
    )

    from OICFurniture import (
        create_furniture,
    )

    kwargs = {
        "width": furniture.Width.Value,
        "depth": furniture.Depth.Value,
        "height": furniture.Height.Value,
        "rotation": furniture.RotationAngle.Value,
    }

    mapping = {
        "cabinet_type": "CabinetType",
        "geometry_mode": "GeometryMode",
        "panel_thickness": "PanelThickness",
        "back_thickness": "BackThickness",
        "shelf_count": "ShelfCount",
        "plinth_height": "PlinthHeight",
        "plinth_setback": "PlinthSetback",
        "mount_height": "MountHeight",
        "width_b": "WidthB",
        "depth_b": "DepthB",
        "front_type": "FrontType",
        "front_thickness": "FrontThickness",
        "front_gap": "FrontGap",
        "drawer_count": "DrawerCount",
        "drawer_zone_height": "DrawerZoneHeight",
        "corner_opening_width": "CornerOpeningWidth",
        "blind_box_width": "BlindBoxWidth",
        "blind_filler_width": "BlindFillerWidth",
        "blind_door_filler_width": "BlindDoorFillerWidth",
        "blind_mate_width": "BlindMateWidth",
        "blind_mate_depth": "BlindMateDepth",
        "blind_side": "BlindSide",
    }

    for argument, property_name in mapping.items():
        if property_name not in furniture.PropertiesList:
            continue

        value = getattr(
            furniture,
            property_name,
        )

        if property_name in {
            "CabinetType",
            "GeometryMode",
            "FrontType",
            "BlindSide",
        }:
            kwargs[argument] = str(
                value
            )

        elif property_name in {
            "ShelfCount",
            "DrawerCount",
        }:
            kwargs[argument] = int(
                value
            )

        else:
            kwargs[argument] = (
                value.Value
            )

    new_furniture = create_furniture(
        document=document,
        position=new_position,
        **kwargs,
    )

    new_furniture.Label = (
        furniture.Label
    )

    document.recompute()

    return new_furniture
