"""Logical board-part metadata for OpenInteriorCAD.

Board Parts / Cut List 0.3:
- cabinet-level board material,
- front material,
- edge-band material and thickness,
- logical edge-band assignment per part,
- no geometry changes.
"""

from __future__ import annotations

import json


DEFAULT_BOARD_MATERIAL = "Carcass Board"
DEFAULT_FRONT_MATERIAL = "Front Board"
DEFAULT_BACK_MATERIAL = "Back Board"
DEFAULT_EDGE_MATERIAL = "ABS"


def _mm(value) -> float:
    try:
        return round(float(value.Value), 3)
    except Exception:
        try:
            return round(float(value), 3)
        except Exception:
            return 0.0


def _text(obj, name, default):
    try:
        value = str(getattr(obj, name))
    except Exception:
        return default

    value = value.strip()

    return value if value else default


def _part(
    name: str,
    role: str,
    length: float,
    width: float,
    thickness: float,
    material: str,
    quantity: int = 1,
    edge_material: str = "",
    edge_thickness: float = 0.0,
    edge_length: float = 0.0,
    edge_count: int = 0,
    edge_front: bool = False,
    edge_back: bool = False,
    edge_left: bool = False,
    edge_right: bool = False,
):
    """
    Create one logical production part.

    Edge convention:
    - Front / Back run along the part Length
    - Left / Right run along the part Width

    The old aggregate edge_length / edge_count fields are preserved for
    compatibility, but are recalculated from the explicit edge flags when
    at least one flag is enabled.
    """

    length = round(
        max(
            0.0,
            float(
                length
            ),
        ),
        3,
    )

    width = round(
        max(
            0.0,
            float(
                width
            ),
        ),
        3,
    )

    thickness = round(
        max(
            0.0,
            float(
                thickness
            ),
        ),
        3,
    )

    explicit_edges = any(
        (
            edge_front,
            edge_back,
            edge_left,
            edge_right,
        )
    )

    if explicit_edges:
        edge_count = sum(
            1
            for value in (
                edge_front,
                edge_back,
                edge_left,
                edge_right,
            )
            if value
        )

        edge_length = (
            (length if edge_front else 0.0)
            + (length if edge_back else 0.0)
            + (width if edge_left else 0.0)
            + (width if edge_right else 0.0)
        )

    return {
        "name": name,
        "role": role,
        "length": length,
        "width": width,
        "thickness": thickness,
        "material": material,
        "quantity": int(
            quantity
        ),
        "edge_material": edge_material,
        "edge_thickness": round(
            max(
                0.0,
                float(
                    edge_thickness
                ),
            ),
            3,
        ),
        "edge_length": round(
            max(
                0.0,
                float(
                    edge_length
                ),
            ),
            3,
        ),
        "edge_count": int(
            max(
                0,
                edge_count,
            )
        ),
        "edge_front": bool(
            edge_front
        ),
        "edge_back": bool(
            edge_back
        ),
        "edge_left": bool(
            edge_left
        ),
        "edge_right": bool(
            edge_right
        ),
    }


def _production_materials(obj):
    return {
        "board": _text(
            obj,
            "BoardMaterial",
            DEFAULT_BOARD_MATERIAL,
        ),
        "front": _text(
            obj,
            "FrontMaterial",
            DEFAULT_FRONT_MATERIAL,
        ),
        "back": _text(
            obj,
            "BackMaterial",
            DEFAULT_BACK_MATERIAL,
        ),
        "edge": _text(
            obj,
            "EdgeMaterial",
            DEFAULT_EDGE_MATERIAL,
        ),
        "edge_thickness": _mm(
            getattr(
                obj,
                "EdgeThickness",
                0.8,
            )
        ),
    }


def _standard_parts(obj):
    W = _mm(obj.Width)
    D = _mm(obj.Depth)
    H = _mm(obj.Height)
    T = _mm(obj.PanelThickness)
    BT = _mm(obj.BackThickness)

    materials = _production_materials(obj)

    cabinet_type = str(obj.CabinetType)

    plinth = (
        _mm(obj.PlinthHeight)
        if cabinet_type == "Base"
        else 0.0
    )

    body_h = max(0.0, H - plinth)
    clear_h = max(0.0, body_h - 2.0 * T)

    board = materials["board"]
    back = materials["back"]
    edge = materials["edge"]
    edge_t = materials["edge_thickness"]

    parts = [
        _part(
            "Left Side",
            "Side",
            clear_h,
            D,
            T,
            board,
            edge_material=edge,
            edge_thickness=edge_t,
            edge_length=clear_h,
            edge_count=1,
            edge_front=True,
        ),
        _part(
            "Right Side",
            "Side",
            clear_h,
            D,
            T,
            board,
            edge_material=edge,
            edge_thickness=edge_t,
            edge_length=clear_h,
            edge_count=1,
            edge_front=True,
        ),
        _part(
            "Bottom",
            "Bottom",
            max(0.0, W - 2.0 * T),
            D,
            T,
            board,
            edge_material=edge,
            edge_thickness=edge_t,
            edge_length=max(0.0, W - 2.0 * T),
            edge_count=1,
            edge_front=True,
        ),
        _part(
            "Top",
            "Top",
            max(0.0, W - 2.0 * T),
            D,
            T,
            board,
            edge_material=edge,
            edge_thickness=edge_t,
            edge_length=max(0.0, W - 2.0 * T),
            edge_count=1,
            edge_front=True,
        ),
        _part(
            "Back",
            "Back",
            max(0.0, W - 2.0 * T),
            clear_h,
            BT,
            back,
        ),
    ]

    shelf_count = max(
        0,
        int(
            getattr(
                obj,
                "ShelfCount",
                0,
            )
        ),
    )

    if shelf_count:
        shelf_length = max(
            0.0,
            W - 2.0 * T,
        )

        parts.append(
            _part(
                "Shelf",
                "Shelf",
                shelf_length,
                max(0.0, D - BT),
                T,
                board,
                quantity=shelf_count,
                edge_material=edge,
                edge_thickness=edge_t,
                edge_length=shelf_length,
                edge_count=1,
                edge_front=True,
            )
        )

    if plinth > 0.0:
        plinth_length = max(
            0.0,
            W - 2.0 * T,
        )

        parts.append(
            _part(
                "Plinth",
                "Plinth",
                plinth_length,
                plinth,
                T,
                board,
                edge_material=edge,
                edge_thickness=edge_t,
                edge_length=plinth_length,
                edge_count=1,
                edge_front=True,
            )
        )

    front_type = str(
        getattr(
            obj,
            "FrontType",
            "Open",
        )
    )

    if front_type != "Open":
        front_t = _mm(
            obj.FrontThickness
        )
        gap = _mm(
            obj.FrontGap
        )
        front_h = max(
            0.0,
            H - plinth - 2.0 * gap,
        )

        if front_type == "Double Door":
            front_w = max(
                0.0,
                (W - 3.0 * gap) / 2.0,
            )

            parts.append(
                _part(
                    "Front",
                    "Front",
                    front_h,
                    front_w,
                    front_t,
                    materials["front"],
                    quantity=2,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=2.0 * (front_h + front_w),
                    edge_count=4,
                    edge_front=True,
                    edge_back=True,
                    edge_left=True,
                    edge_right=True,
                )
            )

        elif front_type == "Drawers":
            drawer_count = max(
                1,
                int(
                    getattr(
                        obj,
                        "DrawerCount",
                        3,
                    )
                ),
            )

            front_w = max(
                0.0,
                W - 2.0 * gap,
            )

            front_each_h = max(
                0.0,
                (
                    front_h
                    - (drawer_count - 1) * gap
                )
                / drawer_count,
            )

            parts.append(
                _part(
                    "Drawer Front",
                    "Front",
                    front_each_h,
                    front_w,
                    front_t,
                    materials["front"],
                    quantity=drawer_count,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=2.0 * (
                        front_each_h + front_w
                    ),
                    edge_count=4,
                    edge_front=True,
                    edge_back=True,
                    edge_left=True,
                    edge_right=True,
                )
            )

        else:
            front_w = max(
                0.0,
                W - 2.0 * gap,
            )

            parts.append(
                _part(
                    "Front",
                    "Front",
                    front_h,
                    front_w,
                    front_t,
                    materials["front"],
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=2.0 * (
                        front_h + front_w
                    ),
                    edge_count=4,
                    edge_front=True,
                    edge_back=True,
                    edge_left=True,
                    edge_right=True,
                )
            )

    return parts


def _corner_parts(obj):
    """Mirror the accepted Corner Generator 1.7 production geometry."""

    W = _mm(obj.Width)
    DA = _mm(obj.Depth)
    WB = _mm(obj.WidthB)
    DB = _mm(obj.DepthB)
    H = _mm(obj.Height)
    T = _mm(obj.PanelThickness)
    BT = _mm(obj.BackThickness)

    materials = _production_materials(obj)

    board = materials["board"]
    back = materials["back"]
    front_material = materials["front"]
    edge = materials["edge"]
    edge_t = materials["edge_thickness"]

    cabinet_type = str(obj.CabinetType)

    plinth = (
        _mm(obj.PlinthHeight)
        if cabinet_type == "Corner Base"
        else 0.0
    )

    body_h = max(
        0.0,
        H - plinth,
    )

    clear_h = max(
        0.0,
        body_h - 2.0 * T,
    )

    parts = [
        {
            **_part(
                "Bottom",
                "Bottom",
                W,
                WB,
                T,
                board,
                edge_material=edge,
                edge_thickness=edge_t,
                edge_length=max(
                    0.0,
                    W - DB,
                ) + max(
                    0.0,
                    WB - DA,
                ),
                edge_count=2,
            ),
            "shape": "L",
            "edge_pattern": "Custom (L)",
            "cutout_width": max(
                0.0,
                W - DB,
            ),
            "cutout_depth": max(
                0.0,
                WB - DA,
            ),
        },
        {
            **_part(
                "Top",
                "Top",
                W,
                WB,
                T,
                board,
                edge_material=edge,
                edge_thickness=edge_t,
                edge_length=max(
                    0.0,
                    W - DB,
                ) + max(
                    0.0,
                    WB - DA,
                ),
                edge_count=2,
            ),
            "shape": "L",
            "edge_pattern": "Custom (L)",
            "cutout_width": max(
                0.0,
                W - DB,
            ),
            "cutout_depth": max(
                0.0,
                WB - DA,
            ),
        },
        _part(
            "Back A",
            "Back",
            W,
            clear_h,
            BT,
            back,
        ),
        _part(
            "Back B",
            "Back",
            max(
                0.0,
                WB - BT,
            ),
            clear_h,
            BT,
            back,
        ),
        _part(
            "Side A",
            "Side",
            max(
                0.0,
                DA - BT,
            ),
            clear_h,
            T,
            board,
            edge_material=edge,
            edge_thickness=edge_t,
            edge_length=clear_h,
            edge_count=1,
            edge_front=True,
        ),
        _part(
            "Side B",
            "Side",
            max(
                0.0,
                DB - BT,
            ),
            clear_h,
            T,
            board,
            edge_material=edge,
            edge_thickness=edge_t,
            edge_length=clear_h,
            edge_count=1,
            edge_front=True,
        ),
    ]

    requested = _mm(
        obj.CornerOpeningWidth
    )

    run_a = max(
        0.0,
        W - DB,
    )

    run_b = max(
        0.0,
        WB - DA,
    )

    min_run = min(
        run_a,
        run_b,
    )

    filler = max(
        T,
        min_run - min(
            requested,
            max(
                0.0,
                min_run - T,
            ),
        ),
    )

    filler = min(
        filler,
        max(
            T,
            min_run - T,
        ),
    )

    parts.extend(
        [
            _part(
                "Filler A",
                "Filler",
                clear_h,
                filler,
                T,
                board,
                edge_material=edge,
                edge_thickness=edge_t,
                edge_length=clear_h,
                edge_count=1,
                edge_front=True,
            ),
            _part(
                "Filler B",
                "Filler",
                clear_h,
                filler,
                T,
                board,
                edge_material=edge,
                edge_thickness=edge_t,
                edge_length=clear_h,
                edge_count=1,
                edge_front=True,
            ),
        ]
    )

    shelf_count = max(
        0,
        int(
            getattr(
                obj,
                "ShelfCount",
                0,
            )
        ),
    )

    if shelf_count:
        parts.append(
            {
                **_part(
                    "Shelf",
                    "Shelf",
                    W,
                    WB,
                    T,
                    board,
                    quantity=shelf_count,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=max(
                        0.0,
                        W - DB,
                    ) + max(
                        0.0,
                        WB - DA,
                    ),
                    edge_count=2,
                ),
                "shape": "L",
                "edge_pattern": "Custom (L)",
                "note": (
                    "Stops at the inner faces "
                    "of both fillers."
                ),
            }
        )

    front_type = str(
        getattr(
            obj,
            "FrontType",
            "Open",
        )
    )

    if front_type == "Corner Folding Doors":
        FT = _mm(
            obj.FrontThickness
        )

        gap = _mm(
            obj.FrontGap
        )

        front_h = max(
            0.0,
            H - plinth - 2.0 * gap,
        )

        front_a_len = max(
            0.0,
            W - DB - gap,
        )

        front_b_len = max(
            0.0,
            (WB - gap)
            - (
                DA
                + FT
                + gap
            ),
        )

        parts.extend(
            [
                _part(
                    "Front A",
                    "Front",
                    front_h,
                    front_a_len,
                    FT,
                    front_material,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=2.0 * (
                        front_h + front_a_len
                    ),
                    edge_count=4,
                    edge_front=True,
                    edge_back=True,
                    edge_left=True,
                    edge_right=True,
                ),
                _part(
                    "Front B",
                    "Front",
                    front_h,
                    front_b_len,
                    FT,
                    front_material,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=2.0 * (
                        front_h + front_b_len
                    ),
                    edge_count=4,
                    edge_front=True,
                    edge_back=True,
                    edge_left=True,
                    edge_right=True,
                ),
            ]
        )

    if plinth > 0.0:
        setback = _mm(
            obj.PlinthSetback
        )

        a_y = max(
            BT,
            DA - setback - T,
        )

        b_x = max(
            BT,
            DB - setback - T,
        )

        plinth_a_len = max(
            0.0,
            W - b_x,
        )

        b_y0 = (
            a_y + T
        )

        plinth_b_len = max(
            0.0,
            WB - b_y0,
        )

        parts.extend(
            [
                _part(
                    "Plinth A",
                    "Plinth",
                    plinth_a_len,
                    plinth,
                    T,
                    board,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=plinth_a_len,
                    edge_count=1,
                ),
                _part(
                    "Plinth B",
                    "Plinth",
                    plinth_b_len,
                    plinth,
                    T,
                    board,
                    edge_material=edge,
                    edge_thickness=edge_t,
                    edge_length=plinth_b_len,
                    edge_count=1,
                ),
            ]
        )

    return parts



def _edge_overrides(obj):
    """Return validated per-part edge overrides stored on the cabinet."""

    raw = getattr(
        obj,
        "EdgeOverridesJSON",
        "{}",
    )

    try:
        data = json.loads(
            str(raw)
            if raw
            else "{}"
        )
    except Exception:
        return {}

    return (
        data
        if isinstance(
            data,
            dict,
        )
        else {}
    )


def _apply_edge_overrides(
    obj,
    parts,
):
    """
    Apply user edge overrides after automatic production rules.

    Override key is the logical part name, e.g.:
    "Shelf", "Front A", "Plinth B".

    This deliberately changes metadata only.
    """

    overrides = _edge_overrides(
        obj
    )

    if not overrides:
        return parts

    for part in parts:
        name = str(
            part.get(
                "name",
                "",
            )
        )

        override = overrides.get(
            name
        )

        if not isinstance(
            override,
            dict,
        ):
            continue

        front = bool(
            override.get(
                "front",
                part.get(
                    "edge_front",
                    False,
                ),
            )
        )
        back = bool(
            override.get(
                "back",
                part.get(
                    "edge_back",
                    False,
                ),
            )
        )
        left = bool(
            override.get(
                "left",
                part.get(
                    "edge_left",
                    False,
                ),
            )
        )
        right = bool(
            override.get(
                "right",
                part.get(
                    "edge_right",
                    False,
                ),
            )
        )

        part["edge_front"] = front
        part["edge_back"] = back
        part["edge_left"] = left
        part["edge_right"] = right

        length = float(
            part.get(
                "length",
                0.0,
            )
        )
        width = float(
            part.get(
                "width",
                0.0,
            )
        )

        part["edge_count"] = sum(
            1
            for value in (
                front,
                back,
                left,
                right,
            )
            if value
        )

        part["edge_length"] = round(
            (
                (length if front else 0.0)
                + (length if back else 0.0)
                + (width if left else 0.0)
                + (width if right else 0.0)
            ),
            3,
        )

        if str(
            part.get(
                "edge_pattern",
                "",
            )
        ).startswith(
            "Custom"
        ):
            # Explicit user override takes precedence over automatic
            # custom L-shape label for reporting purposes.
            part["edge_pattern"] = ""

    return parts


def build_board_parts(obj):
    cabinet_type = str(
        getattr(
            obj,
            "CabinetType",
            "",
        )
    )

    if cabinet_type in {
        "Corner Base",
        "Corner Wall",
    }:
        parts = _corner_parts(
            obj
        )
    else:
        parts = _standard_parts(
            obj
        )

    return _apply_edge_overrides(
        obj,
        parts,
    )


def board_parts_json(parts) -> str:
    return json.dumps(
        parts,
        ensure_ascii=False,
        separators=(",", ":"),
    )
