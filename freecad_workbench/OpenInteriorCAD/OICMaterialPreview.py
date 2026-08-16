"""3D hover preview for OpenInteriorCAD material assignment.

Materials 0.4

Color convention:
- Carcass: blue
- Fronts: green
- Backs: violet
- Edge band: orange

The preview is a temporary Coin3D overlay only.
No FreeCAD document objects and no Shape modifications are created.
"""

from __future__ import annotations

import FreeCADGui as Gui
from pivy import coin

from OICBoardParts import build_board_parts
from OICEdgePreview import (
    EdgePreview,
    _add,
    _corner_l_faces,
    _corner_part_rectangles,
    _standard_part_rectangles,
    _transform_point,
)


CATEGORY_CARCASS = "Carcass"
CATEGORY_FRONT = "Front"
CATEGORY_BACK = "Back"
CATEGORY_EDGE = "Edge"

CATEGORY_COLORS = {
    CATEGORY_CARCASS: (
        0.12,
        0.50,
        1.00,
    ),
    CATEGORY_FRONT: (
        0.20,
        0.85,
        0.35,
    ),
    CATEGORY_BACK: (
        0.68,
        0.36,
        1.00,
    ),
    CATEGORY_EDGE: (
        1.00,
        0.35,
        0.03,
    ),
}


def _category_for_part(
    part,
):
    role = str(
        part.get(
            "role",
            "",
        )
    ).strip().lower()

    name = str(
        part.get(
            "name",
            "",
        )
    ).strip().lower()

    combined = (
        role
        + " "
        + name
    )

    if (
        "front" in combined
        or "door" in combined
    ):
        return CATEGORY_FRONT

    if "back" in combined:
        return CATEGORY_BACK

    return CATEGORY_CARCASS


def _box_faces(
    origin,
    u,
    v,
    thickness,
):
    """Return six quadrilateral faces for one rectangular board."""

    p000 = origin
    p100 = _add(
        origin,
        u,
    )
    p010 = _add(
        origin,
        v,
    )
    p110 = _add(
        p100,
        v,
    )

    p001 = _add(
        p000,
        thickness,
    )
    p101 = _add(
        p100,
        thickness,
    )
    p011 = _add(
        p010,
        thickness,
    )
    p111 = _add(
        p110,
        thickness,
    )

    return [
        # Broad faces
        [
            p000,
            p100,
            p110,
            p010,
        ],
        [
            p001,
            p011,
            p111,
            p101,
        ],
        # Narrow faces
        [
            p000,
            p001,
            p101,
            p100,
        ],
        [
            p010,
            p110,
            p111,
            p011,
        ],
        [
            p000,
            p010,
            p011,
            p001,
        ],
        [
            p100,
            p101,
            p111,
            p110,
        ],
    ]


def _part_faces(
    obj,
    part_name,
):
    """
    Return world-space board faces for one logical part.

    Rectangular parts use the same placement logic as Edge Assignment.
    Corner L-shaped Bottom/Top/Shelf use their physical side faces as a
    reliable preview fallback.
    """

    cabinet_type = str(
        getattr(
            obj,
            "CabinetType",
            "",
        )
    )

    local_faces = []

    if cabinet_type in {
        "Corner Base",
        "Corner Wall",
    }:
        if part_name in {
            "Bottom",
            "Top",
            "Shelf",
        }:
            # These are L-shaped boards. EdgePreview already has exact
            # physical side faces for them. Showing all of them makes the
            # L-shaped element clearly identifiable without changing Shape.
            local_faces = _corner_l_faces(
                obj,
                part_name,
                None,
            )
        else:
            rectangles = _corner_part_rectangles(
                obj,
                part_name,
            )

            for origin, u, v, thickness in rectangles:
                local_faces.extend(
                    _box_faces(
                        origin,
                        u,
                        v,
                        thickness,
                    )
                )

    else:
        rectangles = _standard_part_rectangles(
            obj,
            part_name,
        )

        for origin, u, v, thickness in rectangles:
            local_faces.extend(
                _box_faces(
                    origin,
                    u,
                    v,
                    thickness,
                )
            )

    return [
        [
            _transform_point(
                obj,
                point,
            )
            for point in face
        ]
        for face in local_faces
    ]


class MaterialPreview:
    """Temporary color overlay for a selected production material category."""

    FACE_OFFSET = 0.65

    def __init__(
        self,
    ):
        self.root = None
        self.view = None

        # Reuse the stable Edge Assignment renderer for edge-band preview.
        self.edge_preview = EdgePreview()

    def clear(
        self,
    ):
        self.edge_preview.clear()

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
        self.view = None

    def show(
        self,
        obj,
        category,
    ):
        self.clear()

        if obj is None:
            return

        if category == CATEGORY_EDGE:
            self._show_edges(
                obj
            )
            return

        gui_document = Gui.activeDocument()

        if gui_document is None:
            return

        self.view = gui_document.activeView()

        if self.view is None:
            return

        parts = build_board_parts(
            obj
        )

        faces = []

        for part in parts:
            if _category_for_part(
                part
            ) != category:
                continue

            part_name = str(
                part.get(
                    "name",
                    "",
                )
            )

            faces.extend(
                _part_faces(
                    obj,
                    part_name,
                )
            )

        if not faces:
            return

        root = coin.SoSeparator()

        # The preview must stay visible while orbiting.
        try:
            depth = coin.SoDepthBuffer()
            depth.test = False
            depth.write = False
            root.addChild(
                depth
            )
        except Exception:
            pass

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

        light_model = coin.SoLightModel()
        light_model.model = coin.SoLightModel.BASE_COLOR
        root.addChild(
            light_model
        )

        color = CATEGORY_COLORS.get(
            category,
            (
                1.0,
                1.0,
                0.0,
            ),
        )

        root.addChild(
            self._make_faces_node(
                faces,
                color,
            )
        )

        try:
            self.view.getSceneGraph().addChild(
                root
            )
        except Exception:
            return

        self.root = root

    def _show_edges(
        self,
        obj,
    ):
        assignments = {}

        for part in build_board_parts(
            obj
        ):
            part_name = str(
                part.get(
                    "name",
                    "",
                )
            )

            assignments[
                part_name
            ] = {
                "front": bool(
                    part.get(
                        "edge_front",
                        False,
                    )
                ),
                "back": bool(
                    part.get(
                        "edge_back",
                        False,
                    )
                ),
                "left": bool(
                    part.get(
                        "edge_left",
                        False,
                    )
                ),
                "right": bool(
                    part.get(
                        "edge_right",
                        False,
                    )
                ),
            }

        self.edge_preview.show_assignments(
            obj,
            assignments,
        )

    def _offset_face(
        self,
        face,
    ):
        """
        A tiny view-independent offset is unnecessary when depth testing is
        disabled, but keeping coordinates untouched also guarantees correct
        correspondence with the cabinet.
        """
        return face

    def _make_faces_node(
        self,
        faces,
        color,
    ):
        separator = coin.SoSeparator()

        material = coin.SoMaterial()
        material.diffuseColor = color
        material.emissiveColor = tuple(
            min(
                1.0,
                component * 0.40,
            )
            for component in color
        )
        material.transparency = 0.28
        separator.addChild(
            material
        )

        style = coin.SoDrawStyle()
        style.style = coin.SoDrawStyle.FILLED
        separator.addChild(
            style
        )

        points = []
        face_count = 0

        for face in faces:
            if len(
                face
            ) != 4:
                continue

            # Draw both windings so the preview is visible from either side.
            for point in face:
                points.append(
                    (
                        point.x,
                        point.y,
                        point.z,
                    )
                )

            for point in reversed(
                face
            ):
                points.append(
                    (
                        point.x,
                        point.y,
                        point.z,
                    )
                )

            face_count += 2

        coordinates = coin.SoCoordinate3()

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
            face_count,
            [
                4
                for _ in range(
                    face_count
                )
            ],
        )

        separator.addChild(
            face_set
        )

        # Strong outline improves recognition on dark FreeCAD themes.
        outline_material = coin.SoMaterial()
        outline_material.diffuseColor = color
        outline_material.emissiveColor = color
        separator.addChild(
            outline_material
        )

        line_style = coin.SoDrawStyle()
        line_style.style = coin.SoDrawStyle.LINES
        line_style.lineWidth = 3.0
        separator.addChild(
            line_style
        )

        line_points = []
        line_count = 0

        for face in faces:
            if len(
                face
            ) != 4:
                continue

            sequence = [
                face[0],
                face[1],
                face[2],
                face[3],
                face[0],
            ]

            for point in sequence:
                line_points.append(
                    (
                        point.x,
                        point.y,
                        point.z,
                    )
                )

            line_count += 1

        line_coords = coin.SoCoordinate3()

        line_coords.point.setValues(
            0,
            len(
                line_points
            ),
            line_points,
        )

        separator.addChild(
            line_coords
        )

        lines = coin.SoLineSet()
        lines.numVertices.setValues(
            0,
            line_count,
            [
                5
                for _ in range(
                    line_count
                )
            ],
        )

        separator.addChild(
            lines
        )

        return separator
