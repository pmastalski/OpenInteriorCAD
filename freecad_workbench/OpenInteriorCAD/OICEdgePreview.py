"""Temporary exact edge-face preview for OpenInteriorCAD Edge Assignment.

Cut List 0.8:
- highlights the actual narrow side face of the board that receives edge band,
- uses board thickness to build the preview face,
- keeps reliable hover behavior from 0.7,
- creates no document objects and never modifies cabinet Shape.
"""

from __future__ import annotations

import math

import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin


EDGE_FRONT = "front"
EDGE_BACK = "back"
EDGE_LEFT = "left"
EDGE_RIGHT = "right"


def _value(obj, name, default=0.0):
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


def _vector(
    x,
    y,
    z,
):
    return App.Vector(
        float(
            x
        ),
        float(
            y
        ),
        float(
            z
        ),
    )


def _add(
    a,
    b,
):
    return App.Vector(
        a.x + b.x,
        a.y + b.y,
        a.z + b.z,
    )


def _sub(
    a,
    b,
):
    return App.Vector(
        a.x - b.x,
        a.y - b.y,
        a.z - b.z,
    )


def _scale(
    vector,
    factor,
):
    return App.Vector(
        vector.x * factor,
        vector.y * factor,
        vector.z * factor,
    )


def _length(
    vector,
):
    return math.sqrt(
        vector.x * vector.x
        + vector.y * vector.y
        + vector.z * vector.z
    )


def _normalized(
    vector,
):
    length = _length(
        vector
    )

    if length <= 1e-9:
        return App.Vector(
            0.0,
            0.0,
            1.0,
        )

    return _scale(
        vector,
        1.0 / length,
    )


def _cross(
    a,
    b,
):
    return App.Vector(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )


def _transform_point(
    obj,
    point,
):
    placement = getattr(
        obj,
        "Placement",
        None,
    )

    if placement is None:
        return point

    try:
        return placement.multVec(
            point
        )

    except Exception:
        return point


def _transform_vector(
    obj,
    vector,
):
    placement = getattr(
        obj,
        "Placement",
        None,
    )

    if placement is None:
        return vector

    try:
        return placement.Rotation.multVec(
            vector
        )

    except Exception:
        return vector


def _rectangle_edge_faces(
    origin,
    u,
    v,
    thickness_vector,
    edge_name=None,
):
    """
    Return exact narrow edge faces for a rectangular board.

    Board convention:
    - u = Length direction
    - v = Width direction
    - thickness_vector = physical board thickness direction

    Front / Back are edges parallel to U.
    Left / Right are edges parallel to V.
    """

    p00 = origin
    p10 = _add(
        origin,
        u,
    )
    p01 = _add(
        origin,
        v,
    )
    p11 = _add(
        p10,
        v,
    )

    t = thickness_vector

    faces = {
        EDGE_FRONT: [
            p01,
            p11,
            _add(
                p11,
                t,
            ),
            _add(
                p01,
                t,
            ),
        ],
        EDGE_BACK: [
            p00,
            p10,
            _add(
                p10,
                t,
            ),
            _add(
                p00,
                t,
            ),
        ],
        EDGE_LEFT: [
            p00,
            p01,
            _add(
                p01,
                t,
            ),
            _add(
                p00,
                t,
            ),
        ],
        EDGE_RIGHT: [
            p10,
            p11,
            _add(
                p11,
                t,
            ),
            _add(
                p10,
                t,
            ),
        ],
    }

    if edge_name in faces:
        return [
            faces[
                edge_name
            ]
        ]

    return [
        faces[
            key
        ]
        for key in (
            EDGE_FRONT,
            EDGE_BACK,
            EDGE_LEFT,
            EDGE_RIGHT,
        )
    ]


def _standard_front_rectangles(
    obj,
):
    W = _value(
        obj,
        "Width",
    )
    D = _value(
        obj,
        "Depth",
    )
    H = _value(
        obj,
        "Height",
    )
    FT = max(
        0.01,
        _value(
            obj,
            "FrontThickness",
            18.0,
        ),
    )
    gap = max(
        0.0,
        _value(
            obj,
            "FrontGap",
            2.0,
        ),
    )

    cabinet_type = str(
        getattr(
            obj,
            "CabinetType",
            "",
        )
    )

    z0 = (
        max(
            0.0,
            _value(
                obj,
                "PlinthHeight",
            ),
        )
        if cabinet_type in {
            "Base",
            "Tall",
        }
        else 0.0
    )

    front_h = max(
        0.0,
        H - z0 - 2.0 * gap,
    )

    if front_h <= 0.01:
        return []

    front_type = str(
        getattr(
            obj,
            "FrontType",
            "Open",
        )
    )

    # Front thickness extends in Y.
    t = _vector(
        0.0,
        FT,
        0.0,
    )

    if front_type in {
        "Single Door",
        "Lift-up",
        "Door + Drawers",
    }:
        width = max(
            0.0,
            W - 2.0 * gap,
        )

        return [
            (
                _vector(
                    gap,
                    D,
                    z0 + gap,
                ),
                _vector(
                    0.0,
                    0.0,
                    front_h,
                ),
                _vector(
                    width,
                    0.0,
                    0.0,
                ),
                t,
            )
        ]

    if front_type == "Double Door":
        width = max(
            0.0,
            (
                W
                - 3.0 * gap
            )
            / 2.0,
        )

        return [
            (
                _vector(
                    gap,
                    D,
                    z0 + gap,
                ),
                _vector(
                    0.0,
                    0.0,
                    front_h,
                ),
                _vector(
                    width,
                    0.0,
                    0.0,
                ),
                t,
            ),
            (
                _vector(
                    2.0 * gap + width,
                    D,
                    z0 + gap,
                ),
                _vector(
                    0.0,
                    0.0,
                    front_h,
                ),
                _vector(
                    width,
                    0.0,
                    0.0,
                ),
                t,
            ),
        ]

    if front_type == "Drawers":
        count = max(
            1,
            int(
                getattr(
                    obj,
                    "DrawerCount",
                    3,
                )
            ),
        )

        width = max(
            0.0,
            W - 2.0 * gap,
        )

        each_h = max(
            0.0,
            (
                front_h
                - (
                    count - 1
                )
                * gap
            )
            / count,
        )

        result = []
        z = z0 + gap

        for _ in range(
            count
        ):
            result.append(
                (
                    _vector(
                        gap,
                        D,
                        z,
                    ),
                    _vector(
                        0.0,
                        0.0,
                        each_h,
                    ),
                    _vector(
                        width,
                        0.0,
                        0.0,
                    ),
                    t,
                )
            )

            z += (
                each_h
                + gap
            )

        return result

    return []


def _standard_part_rectangles(
    obj,
    part_name,
):
    W = _value(
        obj,
        "Width",
    )
    D = _value(
        obj,
        "Depth",
    )
    H = _value(
        obj,
        "Height",
    )
    T = _value(
        obj,
        "PanelThickness",
        18.0,
    )
    BT = _value(
        obj,
        "BackThickness",
        3.0,
    )

    cabinet_type = str(
        getattr(
            obj,
            "CabinetType",
            "",
        )
    )

    use_plinth = cabinet_type in {
        "Base",
        "Tall",
    }

    plinth = (
        max(
            0.0,
            _value(
                obj,
                "PlinthHeight",
            ),
        )
        if use_plinth
        else 0.0
    )

    body_h = H - plinth
    inner_w = W - 2.0 * T
    inner_d = D - BT
    inner_h = body_h - 2.0 * T

    if min(
        W,
        D,
        H,
        T,
    ) <= 0.01:
        return []

    # Vertical side board: thickness is X.
    if part_name == "Left Side":
        return [
            (
                _vector(
                    0.0,
                    0.0,
                    plinth,
                ),
                _vector(
                    0.0,
                    0.0,
                    body_h,
                ),
                _vector(
                    0.0,
                    D,
                    0.0,
                ),
                _vector(
                    T,
                    0.0,
                    0.0,
                ),
            )
        ]

    if part_name == "Right Side":
        return [
            (
                _vector(
                    W - T,
                    0.0,
                    plinth,
                ),
                _vector(
                    0.0,
                    0.0,
                    body_h,
                ),
                _vector(
                    0.0,
                    D,
                    0.0,
                ),
                _vector(
                    T,
                    0.0,
                    0.0,
                ),
            )
        ]

    # Horizontal boards: thickness is Z.
    if part_name == "Bottom":
        return [
            (
                _vector(
                    T,
                    BT,
                    plinth,
                ),
                _vector(
                    inner_w,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    inner_d,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    T,
                ),
            )
        ]

    if part_name == "Top":
        return [
            (
                _vector(
                    T,
                    BT,
                    plinth + body_h - T,
                ),
                _vector(
                    inner_w,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    inner_d,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    T,
                ),
            )
        ]

    if part_name == "Back":
        return [
            (
                _vector(
                    T,
                    0.0,
                    plinth + T,
                ),
                _vector(
                    inner_w,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    inner_h,
                ),
                _vector(
                    0.0,
                    BT,
                    0.0,
                ),
            )
        ]

    if part_name == "Shelf":
        count = max(
            0,
            int(
                getattr(
                    obj,
                    "ShelfCount",
                    0,
                )
            ),
        )

        if count <= 0:
            return []

        available = (
            inner_h
            - count * T
        )

        if available <= 0.01:
            return []

        gap_z = (
            available
            / (
                count + 1
            )
        )

        z = (
            plinth
            + T
            + gap_z
        )

        result = []

        for _ in range(
            count
        ):
            result.append(
                (
                    _vector(
                        T,
                        BT,
                        z,
                    ),
                    _vector(
                        inner_w,
                        0.0,
                        0.0,
                    ),
                    _vector(
                        0.0,
                        inner_d,
                        0.0,
                    ),
                    _vector(
                        0.0,
                        0.0,
                        T,
                    ),
                )
            )

            z += (
                T
                + gap_z
            )

        return result

    if part_name == "Plinth":
        setback = max(
            0.0,
            _value(
                obj,
                "PlinthSetback",
                50.0,
            ),
        )

        y = max(
            0.0,
            min(
                D - T,
                D - setback - T,
            ),
        )

        return [
            (
                _vector(
                    0.0,
                    y,
                    0.0,
                ),
                _vector(
                    W,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    plinth,
                ),
                _vector(
                    0.0,
                    T,
                    0.0,
                ),
            )
        ]

    if part_name in {
        "Front",
        "Drawer Front",
    }:
        return _standard_front_rectangles(
            obj
        )

    return []


def _corner_layout(
    obj,
):
    W = _value(
        obj,
        "Width",
    )
    DA = _value(
        obj,
        "Depth",
    )
    WB = _value(
        obj,
        "WidthB",
    )
    DB = _value(
        obj,
        "DepthB",
    )
    T = _value(
        obj,
        "PanelThickness",
        18.0,
    )
    opening = max(
        0.0,
        _value(
            obj,
            "CornerOpeningWidth",
            450.0,
        ),
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
        min_run
        - min(
            opening,
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

    return {
        "W": W,
        "DA": DA,
        "WB": WB,
        "DB": DB,
        "T": T,
        "filler": filler,
    }


def _corner_l_faces(
    obj,
    part_name,
    edge_name,
):
    """
    Build exact vertical edge-band faces for L-shaped horizontal boards.

    Because the board lies horizontally, all banded edges are vertical faces
    with height = panel thickness.
    """

    layout = _corner_layout(
        obj
    )

    W = layout["W"]
    DA = layout["DA"]
    WB = layout["WB"]
    DB = layout["DB"]
    T = layout["T"]

    H = _value(
        obj,
        "Height",
    )

    plinth = (
        _value(
            obj,
            "PlinthHeight",
        )
        if str(
            getattr(
                obj,
                "CabinetType",
                "",
            )
        )
        == "Corner Base"
        else 0.0
    )

    if part_name == "Bottom":
        z_values = [
            plinth,
        ]

    elif part_name == "Top":
        z_values = [
            H - T,
        ]

    elif part_name == "Shelf":
        clear_h = (
            H
            - plinth
            - 2.0 * T
        )

        count = max(
            0,
            int(
                getattr(
                    obj,
                    "ShelfCount",
                    0,
                )
            ),
        )

        if count <= 0:
            return []

        free_z = (
            clear_h
            - count * T
        )

        if free_z <= 0.01:
            return []

        gap_z = (
            free_z
            / (
                count + 1
            )
        )

        z = (
            plinth
            + T
            + gap_z
        )

        z_values = []

        for _ in range(
            count
        ):
            z_values.append(
                z
            )

            z += (
                T
                + gap_z
            )

    else:
        return []

    faces = []

    for z in z_values:
        vertical = _vector(
            0.0,
            0.0,
            T,
        )

        per_edge = {
            EDGE_FRONT: [
                [
                    _vector(
                        DB,
                        DA,
                        z,
                    ),
                    _vector(
                        W,
                        DA,
                        z,
                    ),
                    _vector(
                        W,
                        DA,
                        z + T,
                    ),
                    _vector(
                        DB,
                        DA,
                        z + T,
                    ),
                ],
                [
                    _vector(
                        DB,
                        DA,
                        z,
                    ),
                    _vector(
                        DB,
                        WB,
                        z,
                    ),
                    _vector(
                        DB,
                        WB,
                        z + T,
                    ),
                    _vector(
                        DB,
                        DA,
                        z + T,
                    ),
                ],
            ],
            EDGE_BACK: [
                [
                    _vector(
                        0.0,
                        0.0,
                        z,
                    ),
                    _vector(
                        W,
                        0.0,
                        z,
                    ),
                    _vector(
                        W,
                        0.0,
                        z + T,
                    ),
                    _vector(
                        0.0,
                        0.0,
                        z + T,
                    ),
                ],
                [
                    _vector(
                        0.0,
                        0.0,
                        z,
                    ),
                    _vector(
                        0.0,
                        WB,
                        z,
                    ),
                    _vector(
                        0.0,
                        WB,
                        z + T,
                    ),
                    _vector(
                        0.0,
                        0.0,
                        z + T,
                    ),
                ],
            ],
            EDGE_LEFT: [
                [
                    _vector(
                        W,
                        0.0,
                        z,
                    ),
                    _vector(
                        W,
                        DA,
                        z,
                    ),
                    _vector(
                        W,
                        DA,
                        z + T,
                    ),
                    _vector(
                        W,
                        0.0,
                        z + T,
                    ),
                ]
            ],
            EDGE_RIGHT: [
                [
                    _vector(
                        0.0,
                        WB,
                        z,
                    ),
                    _vector(
                        DB,
                        WB,
                        z,
                    ),
                    _vector(
                        DB,
                        WB,
                        z + T,
                    ),
                    _vector(
                        0.0,
                        WB,
                        z + T,
                    ),
                ]
            ],
        }

        if edge_name in per_edge:
            faces.extend(
                per_edge[
                    edge_name
                ]
            )
        else:
            for key in (
                EDGE_FRONT,
                EDGE_BACK,
                EDGE_LEFT,
                EDGE_RIGHT,
            ):
                faces.extend(
                    per_edge[
                        key
                    ]
                )

    return faces


def _corner_part_rectangles(
    obj,
    part_name,
):
    layout = _corner_layout(
        obj
    )

    W = layout["W"]
    DA = layout["DA"]
    WB = layout["WB"]
    DB = layout["DB"]
    T = layout["T"]
    filler = layout["filler"]

    H = _value(
        obj,
        "Height",
    )

    BT = _value(
        obj,
        "BackThickness",
        3.0,
    )

    cabinet_type = str(
        getattr(
            obj,
            "CabinetType",
            "",
        )
    )

    plinth = (
        _value(
            obj,
            "PlinthHeight",
        )
        if cabinet_type == "Corner Base"
        else 0.0
    )

    clear_h = (
        H
        - plinth
        - 2.0 * T
    )

    z0 = plinth + T

    if part_name == "Back A":
        return [
            (
                _vector(
                    0.0,
                    0.0,
                    z0,
                ),
                _vector(
                    W,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    clear_h,
                ),
                _vector(
                    0.0,
                    BT,
                    0.0,
                ),
            )
        ]

    if part_name == "Back B":
        return [
            (
                _vector(
                    0.0,
                    BT,
                    z0,
                ),
                _vector(
                    0.0,
                    WB - BT,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    clear_h,
                ),
                _vector(
                    BT,
                    0.0,
                    0.0,
                ),
            )
        ]

    if part_name == "Side A":
        return [
            (
                _vector(
                    W - T,
                    BT,
                    z0,
                ),
                _vector(
                    0.0,
                    0.0,
                    clear_h,
                ),
                _vector(
                    0.0,
                    DA - BT,
                    0.0,
                ),
                _vector(
                    T,
                    0.0,
                    0.0,
                ),
            )
        ]

    if part_name == "Side B":
        return [
            (
                _vector(
                    BT,
                    WB - T,
                    z0,
                ),
                _vector(
                    0.0,
                    0.0,
                    clear_h,
                ),
                _vector(
                    DB - BT,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    T,
                    0.0,
                ),
            )
        ]

    if part_name == "Filler A":
        return [
            (
                _vector(
                    W - T - filler,
                    DA - T,
                    z0,
                ),
                _vector(
                    0.0,
                    0.0,
                    clear_h,
                ),
                _vector(
                    filler,
                    0.0,
                    0.0,
                ),
                _vector(
                    0.0,
                    T,
                    0.0,
                ),
            )
        ]

    if part_name == "Filler B":
        return [
            (
                _vector(
                    DB - T,
                    WB - T - filler,
                    z0,
                ),
                _vector(
                    0.0,
                    0.0,
                    clear_h,
                ),
                _vector(
                    0.0,
                    filler,
                    0.0,
                ),
                _vector(
                    T,
                    0.0,
                    0.0,
                ),
            )
        ]

    if part_name in {
        "Front A",
        "Front B",
    }:
        FT = max(
            0.01,
            _value(
                obj,
                "FrontThickness",
                18.0,
            ),
        )

        gap = max(
            0.0,
            _value(
                obj,
                "FrontGap",
                2.0,
            ),
        )

        front_h = max(
            0.0,
            H - plinth - 2.0 * gap,
        )

        z = plinth + gap

        if part_name == "Front A":
            length = max(
                0.0,
                W - DB - gap,
            )

            return [
                (
                    _vector(
                        DB,
                        DA,
                        z,
                    ),
                    _vector(
                        0.0,
                        0.0,
                        front_h,
                    ),
                    _vector(
                        length,
                        0.0,
                        0.0,
                    ),
                    _vector(
                        0.0,
                        FT,
                        0.0,
                    ),
                )
            ]

        y0 = (
            DA
            + FT
            + gap
        )

        length = max(
            0.0,
            (
                WB - gap
            )
            - y0,
        )

        return [
            (
                _vector(
                    DB,
                    y0,
                    z,
                ),
                _vector(
                    0.0,
                    0.0,
                    front_h,
                ),
                _vector(
                    0.0,
                    length,
                    0.0,
                ),
                _vector(
                    FT,
                    0.0,
                    0.0,
                ),
            )
        ]

    if part_name in {
        "Plinth A",
        "Plinth B",
    }:
        setback = max(
            0.0,
            _value(
                obj,
                "PlinthSetback",
                50.0,
            ),
        )

        a_y = max(
            BT,
            DA - setback - T,
        )

        b_x = max(
            BT,
            DB - setback - T,
        )

        if part_name == "Plinth A":
            a_len = max(
                0.0,
                W - b_x,
            )

            return [
                (
                    _vector(
                        b_x,
                        a_y,
                        0.0,
                    ),
                    _vector(
                        a_len,
                        0.0,
                        0.0,
                    ),
                    _vector(
                        0.0,
                        0.0,
                        plinth,
                    ),
                    _vector(
                        0.0,
                        T,
                        0.0,
                    ),
                )
            ]

        b_y0 = (
            a_y + T
        )

        b_len = max(
            0.0,
            WB - b_y0,
        )

        return [
            (
                _vector(
                    b_x,
                    b_y0,
                    0.0,
                ),
                _vector(
                    0.0,
                    b_len,
                    0.0,
                ),
                _vector(
                    0.0,
                    0.0,
                    plinth,
                ),
                _vector(
                    T,
                    0.0,
                    0.0,
                ),
            )
        ]

    return []


def preview_faces(
    obj,
    part_name,
    edge_name=None,
):
    """
    Return world-space quadrilateral faces for the selected logical edge.

    Each face is exactly the physical side face created by:
    board edge length x board thickness.
    """

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
        if part_name in {
            "Bottom",
            "Top",
            "Shelf",
        }:
            local_faces = _corner_l_faces(
                obj,
                part_name,
                edge_name,
            )
        else:
            rectangles = _corner_part_rectangles(
                obj,
                part_name,
            )

            local_faces = []

            for origin, u, v, thickness_vector in rectangles:
                local_faces.extend(
                    _rectangle_edge_faces(
                        origin,
                        u,
                        v,
                        thickness_vector,
                        edge_name,
                    )
                )

    else:
        rectangles = _standard_part_rectangles(
            obj,
            part_name,
        )

        local_faces = []

        for origin, u, v, thickness_vector in rectangles:
            local_faces.extend(
                _rectangle_edge_faces(
                    origin,
                    u,
                    v,
                    thickness_vector,
                    edge_name,
                )
            )

    world_faces = []

    for face in local_faces:
        world_faces.append(
            [
                _transform_point(
                    obj,
                    point,
                )
                for point in face
            ]
        )

    return world_faces


class EdgePreview:
    """
    Interactive edge-band preview.

    When Edge Assignment opens:
    - active edge bands are shown in orange,
    - inactive candidate faces are shown in translucent grey,
    - hovered face is shown in bright yellow,
    - clicking a preview face toggles that edge assignment.

    Everything is Coin3D only. No FreeCAD document object is created.
    """

    ACTIVE_COLOR = (
        1.0,
        0.32,
        0.02,
    )

    INACTIVE_COLOR = (
        0.65,
        0.65,
        0.65,
    )

    HOVER_COLOR = (
        1.0,
        0.85,
        0.05,
    )

    FACE_OFFSET = 0.75

    def __init__(
        self,
        on_face_clicked=None,
    ):
        self.root = None
        self.view = None
        self.mouse_callback = None

        self.on_face_clicked = on_face_clicked

        self.obj = None
        self.assignments = {}
        self.hover_target = None

        self.pick_targets = {}

    # ======================================================
    # PUBLIC
    # ======================================================

    def set_click_callback(
        self,
        callback,
    ):
        self.on_face_clicked = callback

    def clear(
        self,
    ):
        self._remove_mouse_callback()

        if (
            self.root is not None
            and self.view is not None
        ):
            try:
                scene = self.view.getSceneGraph()

                scene.removeChild(
                    self.root
                )

            except Exception:
                pass

        self.root = None
        self.view = None
        self.obj = None
        self.pick_targets = {}

    def show_assignments(
        self,
        obj,
        assignments,
        hover_target=None,
    ):
        """
        Display all four candidate edge faces for every logical part.

        assignments:
            {
                "Shelf": {
                    "front": True,
                    "back": False,
                    ...
                },
                ...
            }
        """

        self.obj = obj

        self.assignments = {
            str(
                part_name
            ): {
                str(
                    edge_name
                ): bool(
                    value
                )
                for edge_name, value in edge_values.items()
            }
            for part_name, edge_values in assignments.items()
        }

        self.hover_target = hover_target

        self._rebuild_overlay()

    def set_hover(
        self,
        part_name=None,
        edge_name=None,
    ):
        if part_name is None:
            target = None
        else:
            target = (
                str(
                    part_name
                ),
                (
                    str(
                        edge_name
                    )
                    if edge_name is not None
                    else None
                ),
            )

        if target == self.hover_target:
            return

        self.hover_target = target

        self._rebuild_overlay()

    # ======================================================
    # BUILD
    # ======================================================

    def _rebuild_overlay(
        self,
    ):
        self._remove_mouse_callback()

        if (
            self.root is not None
            and self.view is not None
        ):
            try:
                self.view.getSceneGraph().removeChild(
                    self.root
                )
            except Exception:
                pass

        self.root = None
        self.pick_targets = {}

        if self.obj is None:
            return

        gui_document = Gui.activeDocument()

        if gui_document is None:
            return

        self.view = gui_document.activeView()

        if self.view is None:
            return

        root = coin.SoSeparator()

        # --------------------------------------------------
        # PREVIEW VISIBILITY
        # --------------------------------------------------
        # The edge faces are intentionally drawn as an overlay.
        #
        # In 0.9 the preview could disappear while orbiting because the
        # highlighted face occupied almost the same depth as the cabinet face
        # and was still participating in the normal depth test.
        #
        # Disable depth testing/writing for the preview group when Coin
        # provides SoDepthBuffer. This keeps edge indicators visible from
        # every camera angle and does not affect the cabinet geometry.
        try:
            depth = coin.SoDepthBuffer()
            depth.test = False
            depth.write = False
            root.addChild(
                depth
            )
        except Exception:
            pass

        # Explicitly disable back-face assumptions. Some edge faces are viewed
        # from the opposite side while the cabinet is rotated.
        try:
            hints = coin.SoShapeHints()
            hints.vertexOrdering = coin.SoShapeHints.UNKNOWN_ORDERING
            hints.shapeType = coin.SoShapeHints.UNKNOWN_SHAPE_TYPE
            hints.faceType = coin.SoShapeHints.UNKNOWN_FACE_TYPE
            root.addChild(
                hints
            )
        except Exception:
            pass

        # Render after the normal cabinet geometry and keep both sides visible.
        light_model = coin.SoLightModel()
        light_model.model = coin.SoLightModel.BASE_COLOR
        root.addChild(
            light_model
        )

        pick_id = 0

        for part_name, edge_values in self.assignments.items():
            for edge_name in (
                EDGE_FRONT,
                EDGE_BACK,
                EDGE_LEFT,
                EDGE_RIGHT,
            ):
                faces = preview_faces(
                    self.obj,
                    part_name,
                    edge_name,
                )

                if not faces:
                    continue

                active = bool(
                    edge_values.get(
                        edge_name,
                        False,
                    )
                )

                hovered = (
                    self.hover_target is not None
                    and self.hover_target[0] == part_name
                    and (
                        self.hover_target[1] is None
                        or self.hover_target[1] == edge_name
                    )
                )

                if hovered:
                    color = self.HOVER_COLOR
                    transparency = 0.0
                elif active:
                    color = self.ACTIVE_COLOR
                    transparency = 0.05
                else:
                    color = self.INACTIVE_COLOR
                    transparency = 0.72

                pick_id += 1

                node_name = (
                    f"OICEDGE_{pick_id}"
                )

                self.pick_targets[
                    node_name
                ] = (
                    part_name,
                    edge_name,
                )

                separator = self._make_faces_node(
                    faces,
                    color,
                    transparency,
                    node_name,
                    strong_outline=(
                        hovered
                        or active
                    ),
                )

                root.addChild(
                    separator
                )

        try:
            scene = self.view.getSceneGraph()
            scene.addChild(
                root
            )

        except Exception:
            return

        self.root = root

        self._install_mouse_callback()

    def _offset_face(
        self,
        face,
    ):
        """
        Move the preview fractionally away from the real face.

        This removes z-fighting and also makes Coin picking more reliable.
        """

        if len(
            face
        ) < 4:
            return face

        edge_a = _sub(
            face[1],
            face[0],
        )

        edge_b = _sub(
            face[3],
            face[0],
        )

        normal = _normalized(
            _cross(
                edge_a,
                edge_b,
            )
        )

        offset = _scale(
            normal,
            self.FACE_OFFSET,
        )

        return [
            _add(
                point,
                offset,
            )
            for point in face
        ]

    def _make_faces_node(
        self,
        faces,
        color,
        transparency,
        node_name,
        strong_outline=False,
    ):
        separator = coin.SoSeparator()

        try:
            separator.setName(
                node_name
            )
        except Exception:
            pass

        material = coin.SoMaterial()
        material.diffuseColor = color
        material.emissiveColor = tuple(
            min(
                1.0,
                component * 0.35,
            )
            for component in color
        )
        material.transparency = transparency
        separator.addChild(
            material
        )

        style = coin.SoDrawStyle()
        style.style = coin.SoDrawStyle.FILLED
        separator.addChild(
            style
        )

        coordinates = coin.SoCoordinate3()

        points = []

        offset_faces = []

        for face in faces:
            offset_face = self._offset_face(
                face
            )

            offset_faces.append(
                offset_face
            )

            # Front winding.
            for point in offset_face:
                points.append(
                    (
                        point.x,
                        point.y,
                        point.z,
                    )
                )

            # Reverse winding = the same physical face visible from the
            # opposite camera side. This avoids back-face disappearance on
            # Coin/OpenGL combinations that still cull one winding.
            for point in reversed(
                offset_face
            ):
                points.append(
                    (
                        point.x,
                        point.y,
                        point.z,
                    )
                )

        coordinates.point.setValues(
            0,
            len(
                points
            ),
            points,
        )

        separator.addChild(
            coordinates
        )

        face_set = coin.SoFaceSet()

        face_set.numVertices.setValues(
            0,
            len(
                offset_faces
            )
            * 2,
            [
                4
                for _ in range(
                    len(
                        offset_faces
                    )
                    * 2
                )
            ],
        )

        separator.addChild(
            face_set
        )

        if strong_outline:
            outline_separator = coin.SoSeparator()

            outline_material = coin.SoMaterial()
            outline_material.diffuseColor = color
            outline_material.emissiveColor = color
            outline_separator.addChild(
                outline_material
            )

            line_style = coin.SoDrawStyle()
            line_style.style = coin.SoDrawStyle.LINES
            line_style.lineWidth = (
                4.0
                if strong_outline
                else 2.0
            )

            outline_separator.addChild(
                line_style
            )

            outline_coords = coin.SoCoordinate3()

            outline_points = []

            for face in offset_faces:
                outline_points.extend(
                    [
                        (
                            face[0].x,
                            face[0].y,
                            face[0].z,
                        ),
                        (
                            face[1].x,
                            face[1].y,
                            face[1].z,
                        ),
                        (
                            face[2].x,
                            face[2].y,
                            face[2].z,
                        ),
                        (
                            face[3].x,
                            face[3].y,
                            face[3].z,
                        ),
                        (
                            face[0].x,
                            face[0].y,
                            face[0].z,
                        ),
                    ]
                )

            outline_coords.point.setValues(
                0,
                len(
                    outline_points
                ),
                outline_points,
            )

            outline_separator.addChild(
                outline_coords
            )

            lines = coin.SoLineSet()

            lines.numVertices.setValues(
                0,
                len(
                    offset_faces
                ),
                [
                    5
                    for _ in offset_faces
                ],
            )

            outline_separator.addChild(
                lines
            )

            separator.addChild(
                outline_separator
            )

        return separator

    # ======================================================
    # MODEL CLICK
    # ======================================================

    def _install_mouse_callback(
        self,
    ):
        if self.view is None:
            return

        try:
            self.mouse_callback = self.view.addEventCallback(
                "SoMouseButtonEvent",
                self._mouse_event,
            )

        except Exception:
            self.mouse_callback = None

    def _remove_mouse_callback(
        self,
    ):
        if (
            self.view is not None
            and self.mouse_callback is not None
        ):
            try:
                self.view.removeEventCallback(
                    "SoMouseButtonEvent",
                    self.mouse_callback,
                )

            except Exception:
                pass

        self.mouse_callback = None

    def _mouse_event(
        self,
        info,
    ):
        if (
            self.root is None
            or self.view is None
        ):
            return

        if info.get(
            "State"
        ) != "DOWN":
            return

        if info.get(
            "Button"
        ) != "BUTTON1":
            return

        position = info.get(
            "Position"
        )

        if position is None:
            return

        target = self._pick_target(
            position
        )

        if target is None:
            return

        part_name, edge_name = target

        if self.on_face_clicked is not None:
            try:
                self.on_face_clicked(
                    part_name,
                    edge_name,
                )

            except Exception as error:
                App.Console.PrintError(
                    "OpenInteriorCAD edge click error: "
                    f"{error}\n"
                )

    def _viewport_region(
        self,
    ):
        """
        Retrieve Coin viewport region across FreeCAD/Pivy versions.
        """

        viewer = self.view.getViewer()

        # FreeCAD 1.x usually exposes the render manager this way.
        try:
            manager = viewer.getSoRenderManager()

            return manager.getViewportRegion()

        except Exception:
            pass

        try:
            manager = viewer.getRenderManager()

            return manager.getViewportRegion()

        except Exception:
            pass

        return None

    def _viewport_height(
        self,
        viewport,
    ):
        try:
            size = viewport.getViewportSizePixels()

            try:
                return int(
                    size[1]
                )
            except Exception:
                values = size.getValue()

                return int(
                    values[1]
                )

        except Exception:
            return 0

    def _node_name(
        self,
        node,
    ):
        try:
            name = node.getName()

            try:
                return str(
                    name.getString()
                )
            except Exception:
                return str(
                    name
                )

        except Exception:
            return ""

    def _pick_target(
        self,
        position,
    ):
        viewport = self._viewport_region()

        if viewport is None:
            return None

        try:
            x = int(
                position[0]
            )
            y = int(
                position[1]
            )

        except Exception:
            return None

        height = self._viewport_height(
            viewport
        )

        if height > 0:
            y = (
                height
                - y
            )

        try:
            action = coin.SoRayPickAction(
                viewport
            )

            action.setPoint(
                coin.SbVec2s(
                    x,
                    y,
                )
            )

            action.setRadius(
                4.0
            )

            action.apply(
                self.view.getSceneGraph()
            )

            picked = action.getPickedPoint()

        except Exception:
            return None

        if picked is None:
            return None

        try:
            path = picked.getPath()
            length = path.getLength()

        except Exception:
            return None

        # Search from picked tail towards root for our named separator.
        for index in range(
            length - 1,
            -1,
            -1,
        ):
            try:
                node = path.getNode(
                    index
                )

            except Exception:
                continue

            node_name = self._node_name(
                node
            )

            if node_name in self.pick_targets:
                return self.pick_targets[
                    node_name
                ]

        return None
