"""Persistent hardware library for OpenInteriorCAD.

Hardware 0.2

Stores:
- manufacturer
- code
- name
- hardware type
- unit
- unit price
- notes

The library is stored in FreeCAD preferences and is available across projects.
"""

from __future__ import annotations

import json
import uuid

import FreeCAD as App


PARAM_PATH = (
    "User parameter:BaseApp/Preferences/Mod/"
    "OpenInteriorCAD/Hardware"
)

LIBRARY_KEY = "LibraryJSON"
PRESET_KEY = "PresetsJSON"


TYPE_HINGE = "Hinge"
TYPE_RUNNER = "Drawer Runner"
TYPE_LEG = "Leg"
TYPE_SHELF_SUPPORT = "Shelf Support"
TYPE_LIFT = "Lift-up"
TYPE_HANDLE = "Handle"

HARDWARE_TYPES = [
    TYPE_HINGE,
    TYPE_RUNNER,
    TYPE_LEG,
    TYPE_SHELF_SUPPORT,
    TYPE_LIFT,
    TYPE_HANDLE,
]


DEFAULT_LIBRARY = [
    {
        "id": "generic-hinge",
        "type": TYPE_HINGE,
        "manufacturer": "Generic",
        "code": "HINGE-110",
        "name": "Concealed Hinge 110°",
        "unit": "pcs",
        "price": 0.0,
        "notes": "",
    },
    {
        "id": "generic-runner",
        "type": TYPE_RUNNER,
        "manufacturer": "Generic",
        "code": "RUNNER",
        "name": "Drawer Runner Set",
        "unit": "set",
        "price": 0.0,
        "notes": "",
    },
    {
        "id": "generic-leg",
        "type": TYPE_LEG,
        "manufacturer": "Generic",
        "code": "LEG",
        "name": "Adjustable Leg",
        "unit": "pcs",
        "price": 0.0,
        "notes": "",
    },
    {
        "id": "generic-shelf-support",
        "type": TYPE_SHELF_SUPPORT,
        "manufacturer": "Generic",
        "code": "SHELF-SUPPORT",
        "name": "Shelf Support",
        "unit": "pcs",
        "price": 0.0,
        "notes": "",
    },
    {
        "id": "generic-lift",
        "type": TYPE_LIFT,
        "manufacturer": "Generic",
        "code": "LIFT",
        "name": "Lift-up Mechanism",
        "unit": "set",
        "price": 0.0,
        "notes": "",
    },
    {
        "id": "generic-handle",
        "type": TYPE_HANDLE,
        "manufacturer": "Generic",
        "code": "HANDLE",
        "name": "Handle",
        "unit": "pcs",
        "price": 0.0,
        "notes": "",
    },
]


DEFAULT_PRESETS = [
    {
        "name": "Generic",
        "hinge_id": "generic-hinge",
        "runner_id": "generic-runner",
        "leg_id": "generic-leg",
        "shelf_support_id": "generic-shelf-support",
        "lift_id": "generic-lift",
        "handle_id": "generic-handle",
    },
]


TYPE_TO_KEY = {
    TYPE_HINGE: "hinge_id",
    TYPE_RUNNER: "runner_id",
    TYPE_LEG: "leg_id",
    TYPE_SHELF_SUPPORT: "shelf_support_id",
    TYPE_LIFT: "lift_id",
    TYPE_HANDLE: "handle_id",
}


def _params():
    return App.ParamGet(
        PARAM_PATH
    )


def _float(
    value,
    default=0.0,
):
    try:
        return float(
            value
        )
    except Exception:
        return float(
            default
        )


def normalize_item(
    item,
):
    hardware_type = str(
        item.get(
            "type",
            TYPE_HINGE,
        )
    ).strip()

    if hardware_type not in HARDWARE_TYPES:
        hardware_type = TYPE_HINGE

    item_id = str(
        item.get(
            "id",
            "",
        )
    ).strip()

    if not item_id:
        item_id = str(
            uuid.uuid4()
        )

    unit = str(
        item.get(
            "unit",
            "pcs",
        )
    ).strip()

    if not unit:
        unit = "pcs"

    return {
        "id": item_id,
        "type": hardware_type,
        "manufacturer": str(
            item.get(
                "manufacturer",
                "",
            )
        ).strip(),
        "code": str(
            item.get(
                "code",
                "",
            )
        ).strip(),
        "name": str(
            item.get(
                "name",
                "",
            )
        ).strip(),
        "unit": unit,
        "price": round(
            max(
                0.0,
                _float(
                    item.get(
                        "price",
                        0.0,
                    )
                ),
            ),
            2,
        ),
        "notes": str(
            item.get(
                "notes",
                "",
            )
        ).strip(),
    }


def load_library():
    raw = _params().GetString(
        LIBRARY_KEY,
        "",
    )

    if not raw:
        items = [
            normalize_item(
                item
            )
            for item in DEFAULT_LIBRARY
        ]
        save_library(
            items
        )
        return items

    try:
        data = json.loads(
            raw
        )
    except Exception:
        data = []

    if not isinstance(
        data,
        list,
    ):
        data = []

    items = []

    for item in data:
        if not isinstance(
            item,
            dict,
        ):
            continue

        normalized = normalize_item(
            item
        )

        if normalized[
            "name"
        ]:
            items.append(
                normalized
            )

    if not items:
        items = [
            normalize_item(
                item
            )
            for item in DEFAULT_LIBRARY
        ]
        save_library(
            items
        )

    return items


def save_library(
    items,
):
    normalized = []

    for item in items:
        if not isinstance(
            item,
            dict,
        ):
            continue

        record = normalize_item(
            item
        )

        if record[
            "name"
        ]:
            normalized.append(
                record
            )

    _params().SetString(
        LIBRARY_KEY,
        json.dumps(
            normalized,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ),
    )


def reset_library():
    items = [
        normalize_item(
            item
        )
        for item in DEFAULT_LIBRARY
    ]
    save_library(
        items
    )
    return items


def new_item(
    hardware_type=TYPE_HINGE,
):
    if hardware_type not in HARDWARE_TYPES:
        hardware_type = TYPE_HINGE

    return {
        "id": str(
            uuid.uuid4()
        ),
        "type": hardware_type,
        "manufacturer": "",
        "code": "",
        "name": f"New {hardware_type}",
        "unit": (
            "set"
            if hardware_type in {
                TYPE_RUNNER,
                TYPE_LIFT,
            }
            else "pcs"
        ),
        "price": 0.0,
        "notes": "",
    }


def display_name(
    item,
):
    chunks = []

    manufacturer = str(
        item.get(
            "manufacturer",
            "",
        )
    ).strip()

    code = str(
        item.get(
            "code",
            "",
        )
    ).strip()

    name = str(
        item.get(
            "name",
            "",
        )
    ).strip()

    if manufacturer:
        chunks.append(
            manufacturer
        )

    if code:
        chunks.append(
            code
        )

    if name:
        chunks.append(
            name
        )

    return " | ".join(
        chunks
    )


def find_item(
    items,
    item_id,
):
    item_id = str(
        item_id
    )

    for item in items:
        if str(
            item.get(
                "id",
                "",
            )
        ) == item_id:
            return item

    return None


def items_of_type(
    items,
    hardware_type,
):
    return [
        item
        for item in items
        if item.get(
            "type"
        )
        == hardware_type
    ]


def normalize_preset(
    preset,
):
    result = {
        "name": str(
            preset.get(
                "name",
                "",
            )
        ).strip(),
    }

    for key in TYPE_TO_KEY.values():
        result[
            key
        ] = str(
            preset.get(
                key,
                "",
            )
        ).strip()

    return result


def load_presets():
    raw = _params().GetString(
        PRESET_KEY,
        "",
    )

    if not raw:
        presets = [
            normalize_preset(
                preset
            )
            for preset in DEFAULT_PRESETS
        ]
        save_presets(
            presets
        )
        return presets

    try:
        data = json.loads(
            raw
        )
    except Exception:
        data = []

    if not isinstance(
        data,
        list,
    ):
        data = []

    presets = []

    for preset in data:
        if not isinstance(
            preset,
            dict,
        ):
            continue

        normalized = normalize_preset(
            preset
        )

        if normalized[
            "name"
        ]:
            presets.append(
                normalized
            )

    if not presets:
        presets = [
            normalize_preset(
                preset
            )
            for preset in DEFAULT_PRESETS
        ]
        save_presets(
            presets
        )

    return presets


def save_presets(
    presets,
):
    normalized = []

    for preset in presets:
        if not isinstance(
            preset,
            dict,
        ):
            continue

        record = normalize_preset(
            preset
        )

        if record[
            "name"
        ]:
            normalized.append(
                record
            )

    _params().SetString(
        PRESET_KEY,
        json.dumps(
            normalized,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ),
    )


def reset_presets():
    presets = [
        normalize_preset(
            preset
        )
        for preset in DEFAULT_PRESETS
    ]
    save_presets(
        presets
    )
    return presets
