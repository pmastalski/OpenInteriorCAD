"""Automatic hardware calculation for OpenInteriorCAD.

Hardware 0.1

This module adds production metadata only:
- hinges,
- drawer runners,
- adjustable legs,
- shelf supports,
- lift-up mechanism,
- handles.

It never modifies cabinet Shape geometry.
"""

from __future__ import annotations

import json

import FreeCAD as App

from OICHardwareLibrary import (
    TYPE_HANDLE,
    TYPE_HINGE,
    TYPE_LEG,
    TYPE_LIFT,
    TYPE_RUNNER,
    TYPE_SHELF_SUPPORT,
    find_item,
    load_library,
)


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"

FRONT_OPEN = "Open"
FRONT_SINGLE = "Single Door"
FRONT_DOUBLE = "Double Door"
FRONT_DRAWERS = "Drawers"
FRONT_DOOR_DRAWERS = "Door + Drawers"
FRONT_LIFT_UP = "Lift-up"
FRONT_CORNER_FOLDING = "Corner Folding Doors"

CABINET_BASE = "Base"
CABINET_WALL = "Wall"
CABINET_TALL = "Tall"
CABINET_CORNER_BASE = "Corner Base"
CABINET_CORNER_WALL = "Corner Wall"


HARDWARE_KEY_TO_TYPE = {
    "hinge": TYPE_HINGE,
    "drawer_runner": TYPE_RUNNER,
    "adjustable_leg": TYPE_LEG,
    "shelf_support": TYPE_SHELF_SUPPORT,
    "lift_mechanism": TYPE_LIFT,
    "handle": TYPE_HANDLE,
}


def _float_property(
    obj,
    name,
    default=0.0,
):
    try:
        value = getattr(
            obj,
            name,
        )

        if hasattr(
            value,
            "Value",
        ):
            return float(
                value.Value
            )

        return float(
            value
        )
    except Exception:
        return float(
            default
        )


def _int_property(
    obj,
    name,
    default=0,
):
    try:
        return int(
            getattr(
                obj,
                name,
            )
        )
    except Exception:
        return int(
            default
        )


def _string_property(
    obj,
    name,
    default="",
):
    try:
        return str(
            getattr(
                obj,
                name,
            )
        )
    except Exception:
        return str(
            default
        )


def ensure_hardware_properties(
    obj,
):
    """Add hardware metadata properties to old/new Furniture objects."""

    if getattr(
        obj,
        "OICType",
        "",
    ) != FURNITURE_TYPE:
        return

    if "HardwareOverridesJSON" not in obj.PropertiesList:
        obj.addProperty(
            "App::PropertyString",
            "HardwareOverridesJSON",
            "Production",
            "Manual hardware quantity overrides.",
        )
        obj.HardwareOverridesJSON = "{}"

    if "HardwareSelectionJSON" not in obj.PropertiesList:
        obj.addProperty(
            "App::PropertyString",
            "HardwareSelectionJSON",
            "Production",
            "Selected hardware-library item IDs by hardware key.",
        )
        obj.HardwareSelectionJSON = "{}"

    if "HardwareJSON" not in obj.PropertiesList:
        obj.addProperty(
            "App::PropertyString",
            "HardwareJSON",
            "Production",
            "Calculated hardware list.",
        )
        obj.HardwareJSON = "[]"

        try:
            obj.setEditorMode(
                "HardwareJSON",
                1,
            )
        except Exception:
            pass

    if "HardwareItemCount" not in obj.PropertiesList:
        obj.addProperty(
            "App::PropertyInteger",
            "HardwareItemCount",
            "Production",
            "Number of hardware rows.",
        )
        obj.HardwareItemCount = 0

        try:
            obj.setEditorMode(
                "HardwareItemCount",
                1,
            )
        except Exception:
            pass


def _front_vertical_height(
    obj,
):
    """
    Approximate usable front height using the same cabinet properties
    without changing geometry.
    """

    height = max(
        0.0,
        _float_property(
            obj,
            "Height",
            0.0,
        ),
    )

    cabinet_type = _string_property(
        obj,
        "CabinetType",
        "",
    )

    plinth = max(
        0.0,
        _float_property(
            obj,
            "PlinthHeight",
            0.0,
        ),
    )

    if cabinet_type in {
        CABINET_BASE,
        CABINET_TALL,
        CABINET_CORNER_BASE,
    }:
        return max(
            0.0,
            height - plinth,
        )

    return height


def _hinges_per_leaf(
    leaf_height,
):
    """
    Conservative default hinge count per vertical door leaf.

    These are production defaults, not manufacturer-specific engineering
    calculations. They can be overridden in the Hardware panel.
    """

    height = max(
        0.0,
        float(
            leaf_height
        ),
    )

    if height <= 0.0:
        return 0

    if height <= 900.0:
        return 2

    if height <= 1600.0:
        return 3

    if height <= 2200.0:
        return 4

    return 5


def _leg_count(
    obj,
):
    cabinet_type = _string_property(
        obj,
        "CabinetType",
        "",
    )

    if cabinet_type not in {
        CABINET_BASE,
        CABINET_TALL,
        CABINET_CORNER_BASE,
    }:
        return 0

    width = max(
        0.0,
        _float_property(
            obj,
            "Width",
            0.0,
        ),
    )

    if cabinet_type == CABINET_CORNER_BASE:
        width_b = max(
            0.0,
            _float_property(
                obj,
                "WidthB",
                0.0,
            ),
        )

        if max(
            width,
            width_b,
        ) > 1000.0:
            return 8

        return 6

    if width <= 800.0:
        return 4

    return 6


def _automatic_items(
    obj,
):
    front_type = _string_property(
        obj,
        "FrontType",
        FRONT_OPEN,
    )

    front_height = _front_vertical_height(
        obj
    )

    drawer_count = max(
        1,
        _int_property(
            obj,
            "DrawerCount",
            3,
        ),
    )

    shelf_count = max(
        0,
        _int_property(
            obj,
            "ShelfCount",
            0,
        ),
    )

    hinge_leaves = 0
    handles = 0
    drawer_sets = 0
    lift_sets = 0

    if front_type == FRONT_SINGLE:
        hinge_leaves = 1
        handles = 1

    elif front_type == FRONT_DOUBLE:
        hinge_leaves = 2
        handles = 2

    elif front_type == FRONT_DRAWERS:
        drawer_sets = drawer_count
        handles = drawer_count

    elif front_type == FRONT_DOOR_DRAWERS:
        # Current OpenInteriorCAD front geometry contains one door and one
        # drawer front in this mode.
        hinge_leaves = 1
        drawer_sets = 1
        handles = 2

    elif front_type == FRONT_LIFT_UP:
        lift_sets = 1
        handles = 1

    elif front_type == FRONT_CORNER_FOLDING:
        hinge_leaves = 2
        handles = 2

    hinge_quantity = (
        _hinges_per_leaf(
            front_height
        )
        * hinge_leaves
    )

    legs = _leg_count(
        obj
    )

    shelf_supports = (
        shelf_count
        * 4
    )

    rows = []

    def add(
        key,
        category,
        name,
        unit,
        quantity,
        note="",
    ):
        quantity = int(
            max(
                0,
                quantity,
            )
        )

        if quantity <= 0:
            return

        rows.append(
            {
                "key": key,
                "category": category,
                "name": name,
                "unit": unit,
                "auto_quantity": quantity,
                "quantity": quantity,
                "note": note,
            }
        )

    add(
        "hinge",
        "Front Hardware",
        "Concealed Hinge",
        "pcs",
        hinge_quantity,
        (
            f"{_hinges_per_leaf(front_height)} per leaf"
            if hinge_leaves
            else ""
        ),
    )

    add(
        "drawer_runner",
        "Drawer Hardware",
        "Drawer Runner Set",
        "set",
        drawer_sets,
        "1 set per drawer",
    )

    add(
        "lift_mechanism",
        "Front Hardware",
        "Lift-up Mechanism",
        "set",
        lift_sets,
        "1 set per lift-up front",
    )

    add(
        "adjustable_leg",
        "Cabinet Hardware",
        "Adjustable Leg",
        "pcs",
        legs,
    )

    add(
        "shelf_support",
        "Cabinet Hardware",
        "Shelf Support",
        "pcs",
        shelf_supports,
        "4 per shelf",
    )

    add(
        "handle",
        "Front Hardware",
        "Handle",
        "pcs",
        handles,
        "1 per front element",
    )

    return rows


def load_overrides(
    obj,
):
    ensure_hardware_properties(
        obj
    )

    try:
        raw = str(
            obj.HardwareOverridesJSON
        )
        data = json.loads(
            raw
        )
    except Exception:
        return {}

    if not isinstance(
        data,
        dict,
    ):
        return {}

    result = {}

    for key, value in data.items():
        try:
            quantity = int(
                value
            )
        except Exception:
            continue

        if quantity < 0:
            continue

        result[
            str(
                key
            )
        ] = quantity

    return result


def save_overrides(
    obj,
    overrides,
):
    ensure_hardware_properties(
        obj
    )

    clean = {}

    for key, value in overrides.items():
        try:
            quantity = int(
                value
            )
        except Exception:
            continue

        if quantity < 0:
            continue

        clean[
            str(
                key
            )
        ] = quantity

    obj.HardwareOverridesJSON = json.dumps(
        clean,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )



def load_hardware_selection(
    obj,
):
    ensure_hardware_properties(
        obj
    )

    try:
        data = json.loads(
            str(
                obj.HardwareSelectionJSON
            )
        )
    except Exception:
        return {}

    if not isinstance(
        data,
        dict,
    ):
        return {}

    return {
        str(
            key
        ): str(
            value
        )
        for key, value in data.items()
        if value is not None
    }


def save_hardware_selection(
    obj,
    selection,
):
    ensure_hardware_properties(
        obj
    )

    clean = {
        str(
            key
        ): str(
            value
        )
        for key, value in selection.items()
        if value
    }

    obj.HardwareSelectionJSON = json.dumps(
        clean,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )


def calculate_hardware(
    obj,
):
    """
    Return final hardware rows after overrides and library selections.
    """

    ensure_hardware_properties(
        obj
    )

    rows = _automatic_items(
        obj
    )

    overrides = load_overrides(
        obj
    )

    selection = load_hardware_selection(
        obj
    )

    library = load_library()

    for row in rows:
        key = row[
            "key"
        ]

        if key in overrides:
            row[
                "quantity"
            ] = int(
                overrides[
                    key
                ]
            )
            row[
                "overridden"
            ] = True
        else:
            row[
                "overridden"
            ] = False

        selected_id = selection.get(
            key,
            "",
        )

        item = find_item(
            library,
            selected_id,
        )

        row[
            "library_id"
        ] = selected_id

        if item is not None:
            row[
                "manufacturer"
            ] = item[
                "manufacturer"
            ]
            row[
                "code"
            ] = item[
                "code"
            ]
            row[
                "name"
            ] = item[
                "name"
            ]
            row[
                "unit"
            ] = item[
                "unit"
            ]
            row[
                "unit_price"
            ] = float(
                item[
                    "price"
                ]
            )
            row[
                "item_notes"
            ] = item[
                "notes"
            ]
        else:
            row[
                "manufacturer"
            ] = ""
            row[
                "code"
            ] = ""
            row[
                "unit_price"
            ] = 0.0
            row[
                "item_notes"
            ] = ""

        row[
            "total_price"
        ] = round(
            row[
                "quantity"
            ]
            * row[
                "unit_price"
            ],
            2,
        )

    known = {
        row[
            "key"
        ]
        for row in rows
    }

    definitions = {
        "hinge": (
            "Front Hardware",
            "Concealed Hinge",
            "pcs",
        ),
        "drawer_runner": (
            "Drawer Hardware",
            "Drawer Runner Set",
            "set",
        ),
        "lift_mechanism": (
            "Front Hardware",
            "Lift-up Mechanism",
            "set",
        ),
        "adjustable_leg": (
            "Cabinet Hardware",
            "Adjustable Leg",
            "pcs",
        ),
        "shelf_support": (
            "Cabinet Hardware",
            "Shelf Support",
            "pcs",
        ),
        "handle": (
            "Front Hardware",
            "Handle",
            "pcs",
        ),
    }

    for key, quantity in overrides.items():
        if key in known:
            continue

        if key not in definitions:
            continue

        category, name, unit = definitions[
            key
        ]

        selected_id = selection.get(
            key,
            "",
        )

        item = find_item(
            library,
            selected_id,
        )

        unit_price = 0.0
        manufacturer = ""
        code = ""
        item_notes = ""

        if item is not None:
            manufacturer = item[
                "manufacturer"
            ]
            code = item[
                "code"
            ]
            name = item[
                "name"
            ]
            unit = item[
                "unit"
            ]
            unit_price = float(
                item[
                    "price"
                ]
            )
            item_notes = item[
                "notes"
            ]

        rows.append(
            {
                "key": key,
                "category": category,
                "name": name,
                "unit": unit,
                "auto_quantity": 0,
                "quantity": int(
                    quantity
                ),
                "note": "Manual override",
                "overridden": True,
                "library_id": selected_id,
                "manufacturer": manufacturer,
                "code": code,
                "unit_price": unit_price,
                "total_price": round(
                    int(
                        quantity
                    )
                    * unit_price,
                    2,
                ),
                "item_notes": item_notes,
            }
        )

    rows.sort(
        key=lambda row: (
            row[
                "category"
            ],
            row[
                "name"
            ],
        )
    )

    obj.HardwareJSON = json.dumps(
        rows,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )

    obj.HardwareItemCount = len(
        rows
    )

    return rows

def reset_hardware_overrides(
    obj,
):
    ensure_hardware_properties(
        obj
    )

    obj.HardwareOverridesJSON = "{}"

    return calculate_hardware(
        obj
    )
