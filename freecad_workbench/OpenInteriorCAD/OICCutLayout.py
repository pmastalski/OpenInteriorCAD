"""Board cut-layout calculation for OpenInteriorCAD.

Cut Layout 0.1

This module does not alter FreeCAD geometry. It converts Board Parts into
physical sheet pieces and performs a conservative rectangular shelf packing.

Rectangular parts:
- can be rotated 90 degrees when enabled.

L-shaped corner parts:
- are displayed as L shapes,
- are packed by their rectangular bounding box in 0.1,
- therefore the result is conservative and does not nest other pieces inside
  the L cut-out yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CutPiece:
    cabinet: str
    name: str
    role: str
    material: str
    thickness: float
    length: float
    width: float
    shape: str = "RECT"
    cutout_width: float = 0.0
    cutout_depth: float = 0.0
    edge_material: str = ""
    edge_thickness: float = 0.0
    edge_front: bool = False
    edge_back: bool = False
    edge_left: bool = False
    edge_right: bool = False
    edge_pattern: str = ""
    source_index: int = 0
    copy_index: int = 1


@dataclass
class PlacedPiece:
    piece: CutPiece
    x: float
    y: float
    width: float
    height: float
    rotated: bool = False


@dataclass
class SheetLayout:
    material: str
    thickness: float
    number: int
    sheet_width: float
    sheet_height: float
    margin: float
    kerf: float
    pieces: list[PlacedPiece] = field(
        default_factory=list
    )

    @property
    def usable_width(self):
        return max(
            0.0,
            self.sheet_width
            - 2.0 * self.margin,
        )

    @property
    def usable_height(self):
        return max(
            0.0,
            self.sheet_height
            - 2.0 * self.margin,
        )

    @property
    def used_area(self):
        return sum(
            item.width * item.height
            for item in self.pieces
        )

    @property
    def sheet_area(self):
        return (
            self.sheet_width
            * self.sheet_height
        )

    @property
    def utilization(self):
        if self.sheet_area <= 0.0:
            return 0.0

        return (
            self.used_area
            / self.sheet_area
        )


def _float(value):
    try:
        return float(
            value
        )
    except Exception:
        return 0.0


def expand_board_parts(
    furniture_objects,
    build_board_parts,
):
    """Expand logical Board Parts quantities into physical pieces."""

    pieces = []
    source_index = 0

    for cabinet in furniture_objects:
        cabinet_label = str(
            getattr(
                cabinet,
                "Label",
                getattr(
                    cabinet,
                    "Name",
                    "Cabinet",
                ),
            )
        )

        for part in build_board_parts(
            cabinet
        ):
            quantity = max(
                1,
                int(
                    part.get(
                        "quantity",
                        1,
                    )
                    or 1
                ),
            )

            length = max(
                0.0,
                _float(
                    part.get(
                        "length",
                        0.0,
                    )
                ),
            )

            width = max(
                0.0,
                _float(
                    part.get(
                        "width",
                        0.0,
                    )
                ),
            )

            thickness = max(
                0.0,
                _float(
                    part.get(
                        "thickness",
                        0.0,
                    )
                ),
            )

            material = str(
                part.get(
                    "material",
                    "",
                )
                or "Unspecified"
            )

            shape = str(
                part.get(
                    "shape",
                    "RECT",
                )
                or "RECT"
            ).upper()

            if (
                length <= 0.001
                or width <= 0.001
            ):
                continue

            for copy_index in range(
                1,
                quantity + 1,
            ):
                source_index += 1

                pieces.append(
                    CutPiece(
                        cabinet=cabinet_label,
                        name=str(
                            part.get(
                                "name",
                                "Part",
                            )
                        ),
                        role=str(
                            part.get(
                                "role",
                                "",
                            )
                        ),
                        material=material,
                        thickness=thickness,
                        length=length,
                        width=width,
                        shape=shape,
                        cutout_width=max(
                            0.0,
                            _float(
                                part.get(
                                    "cutout_width",
                                    0.0,
                                )
                            ),
                        ),
                        cutout_depth=max(
                            0.0,
                            _float(
                                part.get(
                                    "cutout_depth",
                                    0.0,
                                )
                            ),
                        ),
                        edge_material=str(
                            part.get(
                                "edge_material",
                                "",
                            )
                            or ""
                        ),
                        edge_thickness=max(
                            0.0,
                            _float(
                                part.get(
                                    "edge_thickness",
                                    0.0,
                                )
                            ),
                        ),
                        edge_front=bool(
                            part.get(
                                "edge_front",
                                False,
                            )
                        ),
                        edge_back=bool(
                            part.get(
                                "edge_back",
                                False,
                            )
                        ),
                        edge_left=bool(
                            part.get(
                                "edge_left",
                                False,
                            )
                        ),
                        edge_right=bool(
                            part.get(
                                "edge_right",
                                False,
                            )
                        ),
                        edge_pattern=str(
                            part.get(
                                "edge_pattern",
                                "",
                            )
                            or ""
                        ),
                        source_index=source_index,
                        copy_index=copy_index,
                    )
                )

    return pieces


def group_pieces(
    pieces,
):
    """Group physical pieces by material and thickness."""

    groups = {}

    for piece in pieces:
        key = (
            piece.material,
            round(
                piece.thickness,
                3,
            ),
        )

        groups.setdefault(
            key,
            [],
        ).append(
            piece
        )

    return groups


def _orientation_options(
    piece,
    allow_rotation,
):
    options = [
        (
            piece.length,
            piece.width,
            False,
        )
    ]

    if (
        allow_rotation
        and abs(
            piece.length
            - piece.width
        )
        > 0.001
    ):
        options.append(
            (
                piece.width,
                piece.length,
                True,
            )
        )

    return options


class _Shelf:
    def __init__(
        self,
        y,
        height,
        x,
    ):
        self.y = y
        self.height = height
        self.x = x


class _SheetState:
    def __init__(
        self,
        sheet,
    ):
        self.sheet = sheet
        self.shelves = []

    def try_place(
        self,
        piece,
        allow_rotation,
    ):
        sheet = self.sheet
        max_x = (
            sheet.sheet_width
            - sheet.margin
        )
        max_y = (
            sheet.sheet_height
            - sheet.margin
        )

        # First try existing shelves.
        best = None

        for shelf_index, shelf in enumerate(
            self.shelves
        ):
            for w, h, rotated in _orientation_options(
                piece,
                allow_rotation,
            ):
                if (
                    h <= shelf.height + 0.001
                    and shelf.x + w <= max_x + 0.001
                ):
                    waste = (
                        shelf.height - h
                    )

                    candidate = (
                        waste,
                        shelf_index,
                        w,
                        h,
                        rotated,
                    )

                    if (
                        best is None
                        or candidate < best
                    ):
                        best = candidate

        if best is not None:
            (
                _waste,
                shelf_index,
                w,
                h,
                rotated,
            ) = best

            shelf = self.shelves[
                shelf_index
            ]

            placed = PlacedPiece(
                piece=piece,
                x=shelf.x,
                y=shelf.y,
                width=w,
                height=h,
                rotated=rotated,
            )

            shelf.x += (
                w
                + sheet.kerf
            )

            sheet.pieces.append(
                placed
            )

            return True

        # Then create a new shelf.
        if self.shelves:
            new_y = (
                self.shelves[-1].y
                + self.shelves[-1].height
                + sheet.kerf
            )
        else:
            new_y = sheet.margin

        candidates = []

        for w, h, rotated in _orientation_options(
            piece,
            allow_rotation,
        ):
            if (
                sheet.margin + w <= max_x + 0.001
                and new_y + h <= max_y + 0.001
            ):
                # Prefer smaller shelf height, then smaller width.
                candidates.append(
                    (
                        h,
                        w,
                        rotated,
                    )
                )

        if not candidates:
            return False

        h, w, rotated = min(
            candidates
        )

        shelf = _Shelf(
            y=new_y,
            height=h,
            x=sheet.margin,
        )

        self.shelves.append(
            shelf
        )

        placed = PlacedPiece(
            piece=piece,
            x=shelf.x,
            y=shelf.y,
            width=w,
            height=h,
            rotated=rotated,
        )

        shelf.x += (
            w
            + sheet.kerf
        )

        sheet.pieces.append(
            placed
        )

        return True


def calculate_layout(
    pieces,
    sheet_width=2800.0,
    sheet_height=2070.0,
    kerf=4.0,
    margin=10.0,
    allow_rotation=True,
):
    """Pack parts into sheets grouped by material and thickness."""

    sheet_width = max(
        1.0,
        float(
            sheet_width
        ),
    )

    sheet_height = max(
        1.0,
        float(
            sheet_height
        ),
    )

    kerf = max(
        0.0,
        float(
            kerf
        ),
    )

    margin = max(
        0.0,
        float(
            margin
        ),
    )

    groups = group_pieces(
        pieces
    )

    layouts = []
    unplaced = []

    for (
        material,
        thickness,
    ), group in sorted(
        groups.items(),
        key=lambda item: (
            item[0][0].lower(),
            item[0][1],
        ),
    ):
        # Largest pieces first.
        ordered = sorted(
            group,
            key=lambda piece: (
                max(
                    piece.length,
                    piece.width,
                ),
                piece.length
                * piece.width,
            ),
            reverse=True,
        )

        states = []

        for piece in ordered:
            placed = False

            # Existing sheets first.
            for state in states:
                if state.try_place(
                    piece,
                    allow_rotation,
                ):
                    placed = True
                    break

            if placed:
                continue

            # New sheet.
            number = (
                len(
                    states
                )
                + 1
            )

            sheet = SheetLayout(
                material=material,
                thickness=thickness,
                number=number,
                sheet_width=sheet_width,
                sheet_height=sheet_height,
                margin=margin,
                kerf=kerf,
            )

            state = _SheetState(
                sheet
            )

            if state.try_place(
                piece,
                allow_rotation,
            ):
                states.append(
                    state
                )
            else:
                unplaced.append(
                    piece
                )

        layouts.extend(
            state.sheet
            for state in states
        )

    return layouts, unplaced
