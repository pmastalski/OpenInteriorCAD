"""Production Cut List panel for OpenInteriorCAD.

Cut List 1.0:
- production categories: Carcass / Fronts / Backs,
- material and thickness grouping,
- board area totals,
- edge-band totals,
- detailed and summary views,
- detailed CSV export,
- production summary CSV export,
- no geometry changes.
"""

from __future__ import annotations

import csv

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from OICBoardParts import build_board_parts


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"

CATEGORY_CARCASS = "Carcass"
CATEGORY_FRONTS = "Fronts"
CATEGORY_BACKS = "Backs"

CATEGORY_ORDER = {
    CATEGORY_CARCASS: 0,
    CATEGORY_FRONTS: 1,
    CATEGORY_BACKS: 2,
}


def _selected_furniture():
    return [
        obj
        for obj in Gui.Selection.getSelection()
        if getattr(
            obj,
            "OICType",
            "",
        )
        == FURNITURE_TYPE
    ]


def _document_furniture():
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


def get_cut_list_source():
    selected = _selected_furniture()

    if selected:
        return selected

    return _document_furniture()


class CutListPanel:
    """Production-ready board and edge-band summary."""

    def __init__(
        self,
        furniture_objects=None,
    ):
        if furniture_objects is None:
            furniture_objects = get_cut_list_source()

        self.furniture_objects = list(
            furniture_objects
        )

        self.raw_rows = []
        self.display_rows = []

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Production Cut List"
        )

        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        self.summary_label = QtWidgets.QLabel()
        self.summary_label.setWordWrap(
            True
        )
        layout.addWidget(
            self.summary_label
        )

        options_row = QtWidgets.QHBoxLayout()

        self.aggregate_checkbox = QtWidgets.QCheckBox(
            "Aggregate identical parts"
        )
        self.aggregate_checkbox.setChecked(
            True
        )
        self.aggregate_checkbox.stateChanged.connect(
            self.refresh
        )

        options_row.addWidget(
            self.aggregate_checkbox
        )

        options_row.addWidget(
            QtWidgets.QLabel(
                "Category:"
            )
        )

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(
            [
                "All",
                CATEGORY_CARCASS,
                CATEGORY_FRONTS,
                CATEGORY_BACKS,
            ]
        )
        self.category_combo.currentIndexChanged.connect(
            self.refresh
        )
        options_row.addWidget(
            self.category_combo
        )

        options_row.addStretch(
            1
        )

        layout.addLayout(
            options_row
        )

        self.tabs = QtWidgets.QTabWidget()

        layout.addWidget(
            self.tabs
        )

        # --------------------------------------------------
        # DETAILED PARTS TAB
        # --------------------------------------------------

        detailed_page = QtWidgets.QWidget()
        detailed_layout = QtWidgets.QVBoxLayout(
            detailed_page
        )

        self.table = QtWidgets.QTableWidget()

        self.columns = [
            "Category",
            "Cabinet",
            "Part",
            "Role",
            "Qty",
            "Length",
            "Width",
            "Thickness",
            "Material",
            "Front",
            "Back",
            "Left",
            "Right",
            "Edge",
            "Edge t.",
            "Edge length",
            "Area",
        ]

        self.table.setColumnCount(
            len(
                self.columns
            )
        )
        self.table.setHorizontalHeaderLabels(
            self.columns
        )
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.table.setAlternatingRowColors(
            True
        )
        self.table.verticalHeader().setVisible(
            False
        )

        detailed_layout.addWidget(
            self.table
        )

        self.tabs.addTab(
            detailed_page,
            "Detailed Parts",
        )

        # --------------------------------------------------
        # MATERIAL SUMMARY TAB
        # --------------------------------------------------

        material_page = QtWidgets.QWidget()
        material_layout = QtWidgets.QVBoxLayout(
            material_page
        )

        self.material_table = QtWidgets.QTableWidget()
        self.material_table.setColumnCount(
            6
        )
        self.material_table.setHorizontalHeaderLabels(
            [
                "Category",
                "Material",
                "Thickness",
                "Parts",
                "Area [m²]",
                "Cabinets",
            ]
        )
        self.material_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.material_table.setAlternatingRowColors(
            True
        )
        self.material_table.verticalHeader().setVisible(
            False
        )

        material_layout.addWidget(
            self.material_table
        )

        self.tabs.addTab(
            material_page,
            "Board Summary",
        )

        # --------------------------------------------------
        # EDGE SUMMARY TAB
        # --------------------------------------------------

        edge_page = QtWidgets.QWidget()
        edge_layout = QtWidgets.QVBoxLayout(
            edge_page
        )

        self.edge_table = QtWidgets.QTableWidget()
        self.edge_table.setColumnCount(
            4
        )
        self.edge_table.setHorizontalHeaderLabels(
            [
                "Edge Material",
                "Thickness",
                "Length [m]",
                "Parts",
            ]
        )
        self.edge_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.edge_table.setAlternatingRowColors(
            True
        )
        self.edge_table.verticalHeader().setVisible(
            False
        )

        edge_layout.addWidget(
            self.edge_table
        )

        self.tabs.addTab(
            edge_page,
            "Edge Summary",
        )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

        button_row = QtWidgets.QHBoxLayout()

        self.refresh_button = QtWidgets.QPushButton(
            "Refresh"
        )
        self.refresh_button.clicked.connect(
            self.refresh
        )
        button_row.addWidget(
            self.refresh_button
        )

        self.export_detailed_button = QtWidgets.QPushButton(
            "Export Detailed CSV"
        )
        self.export_detailed_button.clicked.connect(
            self.export_detailed_csv
        )
        button_row.addWidget(
            self.export_detailed_button
        )

        self.export_summary_button = QtWidgets.QPushButton(
            "Export Production Summary CSV"
        )
        self.export_summary_button.clicked.connect(
            self.export_summary_csv
        )
        button_row.addWidget(
            self.export_summary_button
        )

        button_row.addStretch(
            1
        )
        layout.addLayout(
            button_row
        )

        self.refresh()

    # ======================================================
    # BASIC HELPERS
    # ======================================================

    def _cabinet_label(
        self,
        obj,
    ):
        return str(
            getattr(
                obj,
                "Label",
                getattr(
                    obj,
                    "Name",
                    "Cabinet",
                ),
            )
        )

    def _float(
        self,
        value,
    ):
        try:
            return float(
                value
            )
        except Exception:
            return 0.0

    def _edge_mark(
        self,
        value,
    ):
        return "YES" if value else ""

    def _edge_pattern(
        self,
        part,
    ):
        custom = str(
            part.get(
                "edge_pattern",
                "",
            )
        ).strip()

        if custom:
            return custom

        names = []

        for key, label in (
            ("edge_front", "Front"),
            ("edge_back", "Back"),
            ("edge_left", "Left"),
            ("edge_right", "Right"),
        ):
            if bool(
                part.get(
                    key,
                    False,
                )
            ):
                names.append(
                    label
                )

        return ", ".join(
            names
        )

    def _category(
        self,
        part,
    ):
        """
        Production category based on logical board role/name.

        Keep this independent from geometry creation.
        """

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
            or "drawer front" in combined
        ):
            return CATEGORY_FRONTS

        if "back" in combined:
            return CATEGORY_BACKS

        return CATEGORY_CARCASS

    # ======================================================
    # ROW BUILDING
    # ======================================================

    def _raw_rows(
        self,
    ):
        rows = []

        for furniture in self.furniture_objects:
            try:
                parts = build_board_parts(
                    furniture
                )
            except Exception as error:
                App.Console.PrintError(
                    "OpenInteriorCAD Cut List error: "
                    f"{error}\n"
                )
                continue

            cabinet_label = self._cabinet_label(
                furniture
            )

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

                length = self._float(
                    part.get(
                        "length",
                        0.0,
                    )
                )

                width = self._float(
                    part.get(
                        "width",
                        0.0,
                    )
                )

                thickness = self._float(
                    part.get(
                        "thickness",
                        0.0,
                    )
                )

                edge_length_each = self._float(
                    part.get(
                        "edge_length",
                        0.0,
                    )
                )

                rows.append(
                    {
                        "category": self._category(
                            part
                        ),
                        "cabinet": cabinet_label,
                        "part": str(
                            part.get(
                                "name",
                                "",
                            )
                        ),
                        "role": str(
                            part.get(
                                "role",
                                "",
                            )
                        ),
                        "quantity": quantity,
                        "length": length,
                        "width": width,
                        "thickness": thickness,
                        "material": str(
                            part.get(
                                "material",
                                "",
                            )
                        ),
                        "area": (
                            length
                            * width
                            * quantity
                            / 1_000_000.0
                        ),
                        "edge_material": str(
                            part.get(
                                "edge_material",
                                "",
                            )
                        ),
                        "edge_thickness": self._float(
                            part.get(
                                "edge_thickness",
                                0.0,
                            )
                        ),
                        "edge_length": (
                            edge_length_each
                            * quantity
                            / 1000.0
                        ),
                        "edge_front": bool(
                            part.get(
                                "edge_front",
                                False,
                            )
                        ),
                        "edge_back": bool(
                            part.get(
                                "edge_back",
                                False,
                            )
                        ),
                        "edge_left": bool(
                            part.get(
                                "edge_left",
                                False,
                            )
                        ),
                        "edge_right": bool(
                            part.get(
                                "edge_right",
                                False,
                            )
                        ),
                        "edge_pattern": self._edge_pattern(
                            part
                        ),
                    }
                )

        rows.sort(
            key=lambda row: (
                CATEGORY_ORDER.get(
                    row[
                        "category"
                    ],
                    99,
                ),
                row[
                    "material"
                ],
                row[
                    "thickness"
                ],
                row[
                    "role"
                ],
                row[
                    "length"
                ],
                row[
                    "width"
                ],
            )
        )

        return rows

    def _filtered_rows(
        self,
        rows,
    ):
        category = self.category_combo.currentText()

        if category == "All":
            return list(
                rows
            )

        return [
            row
            for row in rows
            if row[
                "category"
            ]
            == category
        ]

    def _aggregate_rows(
        self,
        rows,
    ):
        grouped = {}

        for row in rows:
            key = (
                row[
                    "category"
                ],
                row[
                    "role"
                ],
                round(
                    row[
                        "length"
                    ],
                    3,
                ),
                round(
                    row[
                        "width"
                    ],
                    3,
                ),
                round(
                    row[
                        "thickness"
                    ],
                    3,
                ),
                row[
                    "material"
                ],
                row[
                    "edge_material"
                ],
                round(
                    row[
                        "edge_thickness"
                    ],
                    3,
                ),
                row[
                    "edge_front"
                ],
                row[
                    "edge_back"
                ],
                row[
                    "edge_left"
                ],
                row[
                    "edge_right"
                ],
                row[
                    "edge_pattern"
                ],
            )

            if key not in grouped:
                grouped[
                    key
                ] = {
                    **row,
                    "cabinet_names": {
                        row[
                            "cabinet"
                        ]
                    },
                    "part_names": {
                        row[
                            "part"
                        ]
                    },
                }

                continue

            target = grouped[
                key
            ]

            target[
                "quantity"
            ] += row[
                "quantity"
            ]

            target[
                "area"
            ] += row[
                "area"
            ]

            target[
                "edge_length"
            ] += row[
                "edge_length"
            ]

            target[
                "cabinet_names"
            ].add(
                row[
                    "cabinet"
                ]
            )

            target[
                "part_names"
            ].add(
                row[
                    "part"
                ]
            )

        result = []

        for source in grouped.values():
            row = dict(
                source
            )

            cabinet_names = sorted(
                row.pop(
                    "cabinet_names"
                )
            )

            part_names = sorted(
                row.pop(
                    "part_names"
                )
            )

            row[
                "cabinet"
            ] = (
                cabinet_names[
                    0
                ]
                if len(
                    cabinet_names
                )
                == 1
                else (
                    f"{len(cabinet_names)} cabinets"
                )
            )

            row[
                "part"
            ] = (
                part_names[
                    0
                ]
                if len(
                    part_names
                )
                == 1
                else " / ".join(
                    part_names
                )
            )

            result.append(
                row
            )

        result.sort(
            key=lambda row: (
                CATEGORY_ORDER.get(
                    row[
                        "category"
                    ],
                    99,
                ),
                row[
                    "material"
                ],
                row[
                    "thickness"
                ],
                row[
                    "role"
                ],
                row[
                    "length"
                ],
                row[
                    "width"
                ],
            )
        )

        return result

    # ======================================================
    # SUMMARIES
    # ======================================================

    def _material_summary_rows(
        self,
        rows,
    ):
        grouped = {}

        for row in rows:
            key = (
                row[
                    "category"
                ],
                row[
                    "material"
                ],
                round(
                    row[
                        "thickness"
                    ],
                    3,
                ),
            )

            target = grouped.setdefault(
                key,
                {
                    "quantity": 0,
                    "area": 0.0,
                    "cabinets": set(),
                },
            )

            target[
                "quantity"
            ] += row[
                "quantity"
            ]

            target[
                "area"
            ] += row[
                "area"
            ]

            target[
                "cabinets"
            ].add(
                row[
                    "cabinet"
                ]
            )

        result = []

        for (
            category,
            material,
            thickness,
        ), data in grouped.items():
            result.append(
                {
                    "category": category,
                    "material": material,
                    "thickness": thickness,
                    "quantity": data[
                        "quantity"
                    ],
                    "area": data[
                        "area"
                    ],
                    "cabinet_count": len(
                        data[
                            "cabinets"
                        ]
                    ),
                }
            )

        result.sort(
            key=lambda row: (
                CATEGORY_ORDER.get(
                    row[
                        "category"
                    ],
                    99,
                ),
                row[
                    "material"
                ],
                row[
                    "thickness"
                ],
            )
        )

        return result

    def _edge_summary_rows(
        self,
        rows,
    ):
        grouped = {}

        for row in rows:
            if (
                not row[
                    "edge_material"
                ]
                or row[
                    "edge_length"
                ]
                <= 0.0
            ):
                continue

            key = (
                row[
                    "edge_material"
                ],
                round(
                    row[
                        "edge_thickness"
                    ],
                    3,
                ),
            )

            target = grouped.setdefault(
                key,
                {
                    "length": 0.0,
                    "parts": 0,
                },
            )

            target[
                "length"
            ] += row[
                "edge_length"
            ]

            target[
                "parts"
            ] += row[
                "quantity"
            ]

        result = []

        for (
            material,
            thickness,
        ), data in grouped.items():
            result.append(
                {
                    "material": material,
                    "thickness": thickness,
                    "length": data[
                        "length"
                    ],
                    "parts": data[
                        "parts"
                    ],
                }
            )

        result.sort(
            key=lambda row: (
                row[
                    "material"
                ],
                row[
                    "thickness"
                ],
            )
        )

        return result

    # ======================================================
    # DISPLAY
    # ======================================================

    def _set_numeric_alignment(
        self,
        item,
    ):
        item.setTextAlignment(
            QtCore.Qt.AlignRight
            | QtCore.Qt.AlignVCenter
        )

    def _populate_detailed_table(
        self,
        rows,
    ):
        self.table.setRowCount(
            len(
                rows
            )
        )

        numeric_columns = {
            4,
            5,
            6,
            7,
            14,
            15,
            16,
        }

        for row_index, row in enumerate(
            rows
        ):
            custom_edge = row[
                "edge_pattern"
            ].startswith(
                "Custom"
            )

            values = [
                row[
                    "category"
                ],
                row[
                    "cabinet"
                ],
                row[
                    "part"
                ],
                row[
                    "role"
                ],
                str(
                    row[
                        "quantity"
                    ]
                ),
                f'{row["length"]:.1f}',
                f'{row["width"]:.1f}',
                f'{row["thickness"]:.1f}',
                row[
                    "material"
                ],
                (
                    row[
                        "edge_pattern"
                    ]
                    if custom_edge
                    else self._edge_mark(
                        row[
                            "edge_front"
                        ]
                    )
                ),
                (
                    ""
                    if custom_edge
                    else self._edge_mark(
                        row[
                            "edge_back"
                        ]
                    )
                ),
                (
                    ""
                    if custom_edge
                    else self._edge_mark(
                        row[
                            "edge_left"
                        ]
                    )
                ),
                (
                    ""
                    if custom_edge
                    else self._edge_mark(
                        row[
                            "edge_right"
                        ]
                    )
                ),
                row[
                    "edge_material"
                ],
                (
                    f'{row["edge_thickness"]:.2f}'
                    if row[
                        "edge_material"
                    ]
                    else ""
                ),
                (
                    f'{row["edge_length"]:.3f}'
                    if row[
                        "edge_material"
                    ]
                    else ""
                ),
                f'{row["area"]:.4f}',
            ]

            for column_index, value in enumerate(
                values
            ):
                item = QtWidgets.QTableWidgetItem(
                    value
                )

                if column_index in numeric_columns:
                    self._set_numeric_alignment(
                        item
                    )

                self.table.setItem(
                    row_index,
                    column_index,
                    item,
                )

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(
            True
        )

    def _populate_material_table(
        self,
        rows,
    ):
        summary = self._material_summary_rows(
            rows
        )

        self.material_table.setRowCount(
            len(
                summary
            )
        )

        for row_index, row in enumerate(
            summary
        ):
            values = [
                row[
                    "category"
                ],
                row[
                    "material"
                ],
                f'{row["thickness"]:.1f}',
                str(
                    row[
                        "quantity"
                    ]
                ),
                f'{row["area"]:.3f}',
                str(
                    row[
                        "cabinet_count"
                    ]
                ),
            ]

            for column_index, value in enumerate(
                values
            ):
                item = QtWidgets.QTableWidgetItem(
                    value
                )

                if column_index >= 2:
                    self._set_numeric_alignment(
                        item
                    )

                self.material_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

        self.material_table.resizeColumnsToContents()
        self.material_table.horizontalHeader().setStretchLastSection(
            True
        )

    def _populate_edge_table(
        self,
        rows,
    ):
        summary = self._edge_summary_rows(
            rows
        )

        self.edge_table.setRowCount(
            len(
                summary
            )
        )

        for row_index, row in enumerate(
            summary
        ):
            values = [
                row[
                    "material"
                ],
                f'{row["thickness"]:.2f}',
                f'{row["length"]:.3f}',
                str(
                    row[
                        "parts"
                    ]
                ),
            ]

            for column_index, value in enumerate(
                values
            ):
                item = QtWidgets.QTableWidgetItem(
                    value
                )

                if column_index >= 1:
                    self._set_numeric_alignment(
                        item
                    )

                self.edge_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

        self.edge_table.resizeColumnsToContents()
        self.edge_table.horizontalHeader().setStretchLastSection(
            True
        )

    def refresh(
        self,
        *_args,
    ):
        current = get_cut_list_source()

        if current:
            self.furniture_objects = current

        raw_rows = self._raw_rows()
        self.raw_rows = raw_rows

        filtered = self._filtered_rows(
            raw_rows
        )

        display = list(
            filtered
        )

        if self.aggregate_checkbox.isChecked():
            display = self._aggregate_rows(
                display
            )

        self.display_rows = display

        self._populate_detailed_table(
            display
        )

        self._populate_material_table(
            filtered
        )

        self._populate_edge_table(
            filtered
        )

        cabinet_count = len(
            {
                row[
                    "cabinet"
                ]
                for row in filtered
            }
        )

        total_quantity = sum(
            row[
                "quantity"
            ]
            for row in filtered
        )

        total_area = sum(
            row[
                "area"
            ]
            for row in filtered
        )

        total_edge = sum(
            row[
                "edge_length"
            ]
            for row in filtered
        )

        category_counts = {}

        for row in filtered:
            category_counts[
                row[
                    "category"
                ]
            ] = (
                category_counts.get(
                    row[
                        "category"
                    ],
                    0,
                )
                + row[
                    "quantity"
                ]
            )

        category_text = "    ".join(
            f"{category}: {category_counts.get(category, 0)}"
            for category in (
                CATEGORY_CARCASS,
                CATEGORY_FRONTS,
                CATEGORY_BACKS,
            )
        )

        if not filtered:
            self.summary_label.setText(
                "No production parts found."
            )

            self.export_detailed_button.setEnabled(
                False
            )

            self.export_summary_button.setEnabled(
                False
            )

        else:
            self.summary_label.setText(
                f"Cabinets: {cabinet_count}    "
                f"Parts: {total_quantity}    "
                f"Board area: {total_area:.3f} m²    "
                f"Edge band: {total_edge:.2f} m\n"
                f"{category_text}"
            )

            self.export_detailed_button.setEnabled(
                True
            )

            self.export_summary_button.setEnabled(
                True
            )

    # ======================================================
    # CSV EXPORT
    # ======================================================

    def _save_path(
        self,
        title,
        default_name,
    ):
        path, _filter = QtWidgets.QFileDialog.getSaveFileName(
            Gui.getMainWindow(),
            title,
            default_name,
            "CSV files (*.csv)",
        )

        if not path:
            return ""

        if not path.lower().endswith(
            ".csv"
        ):
            path += ".csv"

        return path

    def export_detailed_csv(
        self,
    ):
        if not self.display_rows:
            return

        path = self._save_path(
            "Export Detailed Cut List",
            "OpenInteriorCAD_CutList_Detailed.csv",
        )

        if not path:
            return

        try:
            with open(
                path,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:
                writer = csv.writer(
                    csv_file,
                    delimiter=";",
                )

                writer.writerow(
                    [
                        "Category",
                        "Cabinet",
                        "Part",
                        "Role",
                        "Qty",
                        "Length [mm]",
                        "Width [mm]",
                        "Thickness [mm]",
                        "Material",
                        "Edge Front",
                        "Edge Back",
                        "Edge Left",
                        "Edge Right",
                        "Edge Pattern",
                        "Edge Material",
                        "Edge Thickness [mm]",
                        "Edge Length [m]",
                        "Area [m2]",
                    ]
                )

                for row in self.display_rows:
                    writer.writerow(
                        [
                            row[
                                "category"
                            ],
                            row[
                                "cabinet"
                            ],
                            row[
                                "part"
                            ],
                            row[
                                "role"
                            ],
                            row[
                                "quantity"
                            ],
                            f'{row["length"]:.1f}',
                            f'{row["width"]:.1f}',
                            f'{row["thickness"]:.1f}',
                            row[
                                "material"
                            ],
                            self._edge_mark(
                                row[
                                    "edge_front"
                                ]
                            ),
                            self._edge_mark(
                                row[
                                    "edge_back"
                                ]
                            ),
                            self._edge_mark(
                                row[
                                    "edge_left"
                                ]
                            ),
                            self._edge_mark(
                                row[
                                    "edge_right"
                                ]
                            ),
                            row[
                                "edge_pattern"
                            ],
                            row[
                                "edge_material"
                            ],
                            (
                                f'{row["edge_thickness"]:.2f}'
                                if row[
                                    "edge_material"
                                ]
                                else ""
                            ),
                            (
                                f'{row["edge_length"]:.3f}'
                                if row[
                                    "edge_material"
                                ]
                                else ""
                            ),
                            f'{row["area"]:.4f}',
                        ]
                    )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Cut List",
                f"Could not export detailed CSV:\n{error}",
            )
            return

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Cut List",
            f"Detailed CSV exported successfully:\n{path}",
        )

    def export_summary_csv(
        self,
    ):
        filtered = self._filtered_rows(
            self.raw_rows
        )

        if not filtered:
            return

        path = self._save_path(
            "Export Production Summary",
            "OpenInteriorCAD_Production_Summary.csv",
        )

        if not path:
            return

        material_rows = self._material_summary_rows(
            filtered
        )

        edge_rows = self._edge_summary_rows(
            filtered
        )

        try:
            with open(
                path,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:
                writer = csv.writer(
                    csv_file,
                    delimiter=";",
                )

                writer.writerow(
                    [
                        "OPENINTERIORCAD PRODUCTION SUMMARY"
                    ]
                )

                writer.writerow(
                    []
                )

                writer.writerow(
                    [
                        "BOARD MATERIALS"
                    ]
                )

                writer.writerow(
                    [
                        "Category",
                        "Material",
                        "Thickness [mm]",
                        "Parts",
                        "Area [m2]",
                        "Cabinets",
                    ]
                )

                for row in material_rows:
                    writer.writerow(
                        [
                            row[
                                "category"
                            ],
                            row[
                                "material"
                            ],
                            f'{row["thickness"]:.1f}',
                            row[
                                "quantity"
                            ],
                            f'{row["area"]:.3f}',
                            row[
                                "cabinet_count"
                            ],
                        ]
                    )

                writer.writerow(
                    []
                )

                writer.writerow(
                    [
                        "EDGE BANDS"
                    ]
                )

                writer.writerow(
                    [
                        "Material",
                        "Thickness [mm]",
                        "Length [m]",
                        "Parts",
                    ]
                )

                for row in edge_rows:
                    writer.writerow(
                        [
                            row[
                                "material"
                            ],
                            f'{row["thickness"]:.2f}',
                            f'{row["length"]:.3f}',
                            row[
                                "parts"
                            ],
                        ]
                    )

                writer.writerow(
                    []
                )

                writer.writerow(
                    [
                        "TOTALS"
                    ]
                )

                writer.writerow(
                    [
                        "Parts",
                        sum(
                            row[
                                "quantity"
                            ]
                            for row in filtered
                        ),
                    ]
                )

                writer.writerow(
                    [
                        "Board area [m2]",
                        f'{sum(row["area"] for row in filtered):.3f}',
                    ]
                )

                writer.writerow(
                    [
                        "Edge band [m]",
                        f'{sum(row["edge_length"] for row in filtered):.3f}',
                    ]
                )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Cut List",
                f"Could not export production summary:\n{error}",
            )
            return

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Cut List",
            f"Production summary exported successfully:\n{path}",
        )

    # ======================================================
    # TASK PANEL
    # ======================================================

    def getStandardButtons(
        self,
    ):
        return int(
            QtWidgets.QDialogButtonBox.Close
        )

    def reject(
        self,
    ):
        Gui.Control.closeDialog()

        return True

    def accept(
        self,
    ):
        Gui.Control.closeDialog()

        return True
