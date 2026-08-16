"""Persistent material library for OpenInteriorCAD.

Materials 0.1

The library is stored in FreeCAD user preferences, so it is available
between documents and FreeCAD sessions.

This module contains metadata only. It never modifies cabinet geometry.
"""

from __future__ import annotations

import json
import uuid

import FreeCAD as App


PARAM_PATH = (
    "User parameter:BaseApp/Preferences/Mod/"
    "OpenInteriorCAD/Materials"
)

PARAM_KEY = "LibraryJSON"
PRESET_KEY = "PresetsJSON"


TYPE_BOARD = "Board"
TYPE_FRONT = "Front"
TYPE_BACK = "Back"
TYPE_EDGE = "Edge"

MATERIAL_TYPES = [
    TYPE_BOARD,
    TYPE_FRONT,
    TYPE_BACK,
    TYPE_EDGE,
]


DEFAULT_MATERIALS = [
    {
        "id": "default-board",
        "type": TYPE_BOARD,
        "manufacturer": "Generic",
        "code": "CARCASS-18",
        "name": "Carcass Board",
        "thickness": 18.0,
    },
    {
        "id": "default-front",
        "type": TYPE_FRONT,
        "manufacturer": "Generic",
        "code": "FRONT-18",
        "name": "Front Board",
        "thickness": 18.0,
    },
    {
        "id": "default-back",
        "type": TYPE_BACK,
        "manufacturer": "Generic",
        "code": "BACK-3",
        "name": "Back Board",
        "thickness": 3.0,
    },
    {
        "id": "default-edge-08",
        "type": TYPE_EDGE,
        "manufacturer": "Generic",
        "code": "ABS-08",
        "name": "ABS",
        "thickness": 0.8,
    },
    {
        "id": "default-edge-20",
        "type": TYPE_EDGE,
        "manufacturer": "Generic",
        "code": "ABS-20",
        "name": "ABS 2 mm",
        "thickness": 2.0,
    },
]


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


def normalize_material(
    record,
):
    """Return one validated material dictionary."""

    material_type = str(
        record.get(
            "type",
            TYPE_BOARD,
        )
    ).strip()

    if material_type not in MATERIAL_TYPES:
        material_type = TYPE_BOARD

    material_id = str(
        record.get(
            "id",
            "",
        )
    ).strip()

    if not material_id:
        material_id = str(
            uuid.uuid4()
        )

    return {
        "id": material_id,
        "type": material_type,
        "manufacturer": str(
            record.get(
                "manufacturer",
                "",
            )
        ).strip(),
        "code": str(
            record.get(
                "code",
                "",
            )
        ).strip(),
        "name": str(
            record.get(
                "name",
                "",
            )
        ).strip(),
        "thickness": round(
            max(
                0.0,
                _float(
                    record.get(
                        "thickness",
                        0.0,
                    )
                ),
            ),
            3,
        ),
    }


def load_materials():
    """Load persistent material records."""

    raw = _params().GetString(
        PARAM_KEY,
        "",
    )

    if not raw:
        records = [
            normalize_material(
                record
            )
            for record in DEFAULT_MATERIALS
        ]

        save_materials(
            records
        )

        return records

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

    records = []

    for record in data:
        if not isinstance(
            record,
            dict,
        ):
            continue

        normalized = normalize_material(
            record
        )

        if not normalized[
            "name"
        ]:
            continue

        records.append(
            normalized
        )

    if not records:
        records = [
            normalize_material(
                record
            )
            for record in DEFAULT_MATERIALS
        ]

        save_materials(
            records
        )

    return records


def save_materials(
    records,
):
    """Persist material records."""

    normalized = []

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            continue

        item = normalize_material(
            record
        )

        if not item[
            "name"
        ]:
            continue

        normalized.append(
            item
        )

    payload = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )

    _params().SetString(
        PARAM_KEY,
        payload,
    )


def reset_materials():
    records = [
        normalize_material(
            record
        )
        for record in DEFAULT_MATERIALS
    ]

    save_materials(
        records
    )

    return records


def new_material(
    material_type=TYPE_BOARD,
):
    material_type = (
        material_type
        if material_type in MATERIAL_TYPES
        else TYPE_BOARD
    )

    defaults = {
        TYPE_BOARD: (
            "New Board",
            18.0,
        ),
        TYPE_FRONT: (
            "New Front",
            18.0,
        ),
        TYPE_BACK: (
            "New Back",
            3.0,
        ),
        TYPE_EDGE: (
            "New Edge",
            0.8,
        ),
    }

    name, thickness = defaults[
        material_type
    ]

    return {
        "id": str(
            uuid.uuid4()
        ),
        "type": material_type,
        "manufacturer": "",
        "code": "",
        "name": name,
        "thickness": thickness,
    }


def display_name(
    material,
):
    """Readable material label for comboboxes."""

    manufacturer = str(
        material.get(
            "manufacturer",
            "",
        )
    ).strip()

    code = str(
        material.get(
            "code",
            "",
        )
    ).strip()

    name = str(
        material.get(
            "name",
            "",
        )
    ).strip()

    thickness = _float(
        material.get(
            "thickness",
            0.0,
        )
    )

    chunks = []

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

    label = " | ".join(
        chunks
    )

    if thickness > 0.0:
        label += (
            f" | {thickness:g} mm"
        )

    return label


def material_value(
    material,
):
    """
    String written into current Furniture production properties.

    Keep it compact because this value is also shown in Cut List / CSV.
    """

    manufacturer = str(
        material.get(
            "manufacturer",
            "",
        )
    ).strip()

    code = str(
        material.get(
            "code",
            "",
        )
    ).strip()

    name = str(
        material.get(
            "name",
            "",
        )
    ).strip()

    chunks = []

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

    return " ".join(
        chunks
    ).strip()


def find_material(
    records,
    material_id,
):
    material_id = str(
        material_id
    )

    for record in records:
        if str(
            record.get(
                "id",
                "",
            )
        ) == material_id:
            return record

    return None


def materials_of_type(
    records,
    material_type,
):
    return [
        record
        for record in records
        if record.get(
            "type"
        )
        == material_type
    ]



# ============================================================
# MATERIAL PRESETS
# ============================================================

DEFAULT_PRESETS = [
    {
        "name": "Generic 18 mm",
        "board_id": "default-board",
        "front_id": "default-front",
        "back_id": "default-back",
        "edge_id": "default-edge-08",
    },
]


def normalize_preset(
    preset,
):
    """Return one validated material preset dictionary."""

    return {
        "name": str(
            preset.get(
                "name",
                "",
            )
        ).strip(),
        "board_id": str(
            preset.get(
                "board_id",
                "",
            )
        ).strip(),
        "front_id": str(
            preset.get(
                "front_id",
                "",
            )
        ).strip(),
        "back_id": str(
            preset.get(
                "back_id",
                "",
            )
        ).strip(),
        "edge_id": str(
            preset.get(
                "edge_id",
                "",
            )
        ).strip(),
    }


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

        item = normalize_preset(
            preset
        )

        if not item[
            "name"
        ]:
            continue

        normalized.append(
            item
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

        item = normalize_preset(
            preset
        )

        if item[
            "name"
        ]:
            presets.append(
                item
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


def find_preset(
    presets,
    name,
):
    name = str(
        name
    )

    for preset in presets:
        if str(
            preset.get(
                "name",
                "",
            )
        ) == name:
            return preset

    return None
