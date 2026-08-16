"""Production cost calculation for OpenInteriorCAD.

Costing 0.1

Uses existing production metadata:
- Board Parts / Cut List
- Material Library prices
- Edge Library prices
- Hardware Library prices

No geometry changes.
"""

from __future__ import annotations

from collections import defaultdict

import FreeCAD as App
import FreeCADGui as Gui

from OICBoardParts import build_board_parts
from OICHardware import calculate_hardware
from OICMaterialLibrary import (
    TYPE_BACK,
    TYPE_BOARD,
    TYPE_EDGE,
    TYPE_FRONT,
    load_materials,
    material_value,
)


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"


def selected_or_all_furniture():
    selected = [
        obj
        for obj in Gui.Selection.getSelection()
        if getattr(
            obj,
            "OICType",
            "",
        )
        == FURNITURE_TYPE
    ]

    if selected:
        return selected

    document = App.ActiveDocument

    if document is None:
        return []

    return [
        obj
        for obj in document.Objects
        if getattr(
            obj,
            "OICType",
            "",
        )
        == FURNITURE_TYPE
    ]


def _category_for_part(
    part,
):
    role = str(
        part.get(
            "role",
            "",
        )
    ).lower()

    name = str(
        part.get(
            "name",
            "",
        )
    ).lower()

    combined = role + " " + name

    if (
        "front" in combined
        or "door" in combined
    ):
        return "Fronts", TYPE_FRONT

    if "back" in combined:
        return "Backs", TYPE_BACK

    return "Carcass", TYPE_BOARD


def _material_price_map():
    result = {}

    for material in load_materials():
        key = (
            material[
                "type"
            ],
            material_value(
                material
            ),
        )

        result[
            key
        ] = {
            "price": float(
                material.get(
                    "price",
                    0.0,
                )
            ),
            "unit": str(
                material.get(
                    "price_unit",
                    (
                        "m"
                        if material[
                            "type"
                        ] == TYPE_EDGE
                        else "m²"
                    ),
                )
            ),
            "record": material,
        }

    return result


def calculate_project_cost(
    furniture_objects=None,
):
    if furniture_objects is None:
        furniture_objects = selected_or_all_furniture()

    material_prices = _material_price_map()

    rows = []
    totals = defaultdict(
        float
    )

    # ------------------------------------------------------
    # BOARD / FRONT / BACK + EDGE
    # ------------------------------------------------------

    for furniture in furniture_objects:
        cabinet = str(
            getattr(
                furniture,
                "Label",
                "Cabinet",
            )
        )

        try:
            parts = build_board_parts(
                furniture
            )
        except Exception:
            parts = []

        for part in parts:
            quantity = max(
                1,
                int(
                    part.get(
                        "quantity",
                        1,
                    )
                ),
            )

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

            area_m2 = (
                length
                * width
                * quantity
                / 1_000_000.0
            )

            category, material_type = _category_for_part(
                part
            )

            material_name = str(
                part.get(
                    "material",
                    "",
                )
            )

            price_info = material_prices.get(
                (
                    material_type,
                    material_name,
                ),
                {
                    "price": 0.0,
                    "unit": "m²",
                },
            )

            unit_price = float(
                price_info[
                    "price"
                ]
            )

            cost = (
                area_m2
                * unit_price
                if price_info[
                    "unit"
                ] == "m²"
                else 0.0
            )

            rows.append(
                {
                    "cabinet": cabinet,
                    "category": category,
                    "item": material_name,
                    "detail": str(
                        part.get(
                            "name",
                            "",
                        )
                    ),
                    "quantity": area_m2,
                    "unit": "m²",
                    "unit_price": unit_price,
                    "cost": cost,
                }
            )

            totals[
                category
            ] += cost

            edge_material = str(
                part.get(
                    "edge_material",
                    "",
                )
            )

            edge_length_m = (
                float(
                    part.get(
                        "edge_length",
                        0.0,
                    )
                )
                * quantity
                / 1000.0
            )

            if (
                edge_material
                and edge_length_m > 0.0
            ):
                edge_info = material_prices.get(
                    (
                        TYPE_EDGE,
                        edge_material,
                    ),
                    {
                        "price": 0.0,
                        "unit": "m",
                    },
                )

                edge_price = float(
                    edge_info[
                        "price"
                    ]
                )

                edge_cost = (
                    edge_length_m
                    * edge_price
                    if edge_info[
                        "unit"
                    ] == "m"
                    else 0.0
                )

                rows.append(
                    {
                        "cabinet": cabinet,
                        "category": "Edges",
                        "item": edge_material,
                        "detail": str(
                            part.get(
                                "name",
                                "",
                            )
                        ),
                        "quantity": edge_length_m,
                        "unit": "m",
                        "unit_price": edge_price,
                        "cost": edge_cost,
                    }
                )

                totals[
                    "Edges"
                ] += edge_cost

        # --------------------------------------------------
        # HARDWARE
        # --------------------------------------------------

        for hardware in calculate_hardware(
            furniture
        ):
            quantity = int(
                hardware.get(
                    "quantity",
                    0,
                )
            )

            unit_price = float(
                hardware.get(
                    "unit_price",
                    0.0,
                )
            )

            cost = float(
                hardware.get(
                    "total_price",
                    quantity * unit_price,
                )
            )

            rows.append(
                {
                    "cabinet": cabinet,
                    "category": "Hardware",
                    "item": str(
                        hardware.get(
                            "name",
                            "",
                        )
                    ),
                    "detail": " ".join(
                        value
                        for value in (
                            str(
                                hardware.get(
                                    "manufacturer",
                                    "",
                                )
                            ).strip(),
                            str(
                                hardware.get(
                                    "code",
                                    "",
                                )
                            ).strip(),
                        )
                        if value
                    ),
                    "quantity": quantity,
                    "unit": str(
                        hardware.get(
                            "unit",
                            "pcs",
                        )
                    ),
                    "unit_price": unit_price,
                    "cost": cost,
                }
            )

            totals[
                "Hardware"
            ] += cost

    totals[
        "Total"
    ] = sum(
        value
        for key, value in totals.items()
        if key != "Total"
    )

    return rows, dict(
        totals
    )
