"""Cut List panel for OpenInteriorCAD.

Cut List 0.4:
- explicit Front / Back / Left / Right edge-band assignment,
- material-aware cut list,
- aggregation,
- CSV export,
- no geometry changes.
"""

from __future__ import annotations

import csv

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from OICBoardParts import build_board_parts


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"


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
    """Production cut list with explicit edge-band assignment."""

    def __init__(
        self,
        furniture_objects=None,
    ):
        if furniture_objects is None:
            furniture_objects = get_cut_list_source()

        self.furniture_objects = list(
            furniture_objects
        )

        self.display_rows = []

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Cut List"
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
        options_row.addStretch(
            1
        )

        layout.addLayout(
            options_row
        )

        self.table = QtWidgets.QTableWidget()

        self.columns = [
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

        layout.addWidget(
            self.table
        )

        self.materials_label = QtWidgets.QLabel()
        self.materials_label.setWordWrap(
            True
        )
        layout.addWidget(
            self.materials_label
        )

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

        self.export_button = QtWidgets.QPushButton(
            "Export CSV"
        )
        self.export_button.clicked.connect(
            self.export_csv
        )
        button_row.addWidget(
            self.export_button
        )

        button_row.addStretch(
            1
        )
        layout.addLayout(
            button_row
        )

        self.refresh()

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

        return rows

    def _aggregate_rows(
        self,
        rows,
    ):
        grouped = {}

        for row in rows:
            key = (
                row["role"],
                round(
                    row["length"],
                    3,
                ),
                round(
                    row["width"],
                    3,
                ),
                round(
                    row["thickness"],
                    3,
                ),
                row["material"],
                row["edge_material"],
                round(
                    row["edge_thickness"],
                    3,
                ),
                row["edge_front"],
                row["edge_back"],
                row["edge_left"],
                row["edge_right"],
                row["edge_pattern"],
            )

            if key not in grouped:
                grouped[key] = {
                    **row,
                    "cabinet_names": {
                        row["cabinet"]
                    },
                    "part_names": {
                        row["part"]
                    },
                }
                continue

            target = grouped[key]
            target["quantity"] += row["quantity"]
            target["area"] += row["area"]
            target["edge_length"] += row["edge_length"]
            target["cabinet_names"].add(
                row["cabinet"]
            )
            target["part_names"].add(
                row["part"]
            )

        result = []

        for row in grouped.values():
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

            row["cabinet"] = (
                cabinet_names[0]
                if len(
                    cabinet_names
                ) == 1
                else f"{len(cabinet_names)} cabinets"
            )

            row["part"] = (
                part_names[0]
                if len(
                    part_names
                ) == 1
                else " / ".join(
                    part_names
                )
            )

            result.append(
                row
            )

        result.sort(
            key=lambda row: (
                row["material"],
                row["thickness"],
                row["role"],
                row["length"],
                row["width"],
            )
        )

        return result

    def _material_summary(
        self,
        rows,
    ):
        grouped = {}

        for row in rows:
            key = (
                row["material"],
                round(
                    row["thickness"],
                    3,
                ),
            )

            if key not in grouped:
                grouped[key] = {
                    "area": 0.0,
                    "qty": 0,
                }

            grouped[key]["area"] += row["area"]
            grouped[key]["qty"] += row["quantity"]

        items = []

        for (
            material,
            thickness,
        ), data in sorted(
            grouped.items()
        ):
            items.append(
                f"{material} {thickness:.1f} mm: "
                f"{data['qty']} pcs / "
                f"{data['area']:.3f} m²"
            )

        return "    |    ".join(
            items
        )

    def refresh(
        self,
        *_args,
    ):
        current = get_cut_list_source()

        if current:
            self.furniture_objects = current

        raw_rows = self._raw_rows()
        rows = list(
            raw_rows
        )

        if self.aggregate_checkbox.isChecked():
            rows = self._aggregate_rows(
                rows
            )

        self.display_rows = rows

        self.table.setRowCount(
            len(
                rows
            )
        )

        for row_index, row in enumerate(
            rows
        ):
            custom_edge = row["edge_pattern"].startswith(
                "Custom"
            )

            values = [
                row["cabinet"],
                row["part"],
                row["role"],
                str(
                    row["quantity"]
                ),
                f'{row["length"]:.1f}',
                f'{row["width"]:.1f}',
                f'{row["thickness"]:.1f}',
                row["material"],
                (
                    row["edge_pattern"]
                    if custom_edge
                    else self._edge_mark(
                        row["edge_front"]
                    )
                ),
                (
                    ""
                    if custom_edge
                    else self._edge_mark(
                        row["edge_back"]
                    )
                ),
                (
                    ""
                    if custom_edge
                    else self._edge_mark(
                        row["edge_left"]
                    )
                ),
                (
                    ""
                    if custom_edge
                    else self._edge_mark(
                        row["edge_right"]
                    )
                ),
                row["edge_material"],
                (
                    f'{row["edge_thickness"]:.1f}'
                    if row["edge_material"]
                    else ""
                ),
                (
                    f'{row["edge_length"]:.3f}'
                    if row["edge_material"]
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

                if column_index in {
                    3,
                    4,
                    5,
                    6,
                    13,
                    14,
                    15,
                }:
                    item.setTextAlignment(
                        QtCore.Qt.AlignRight
                        | QtCore.Qt.AlignVCenter
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

        cabinet_count = len(
            self.furniture_objects
        )
        total_quantity = sum(
            row["quantity"]
            for row in raw_rows
        )
        total_area = sum(
            row["area"]
            for row in raw_rows
        )
        total_edge = sum(
            row["edge_length"]
            for row in raw_rows
        )

        if cabinet_count == 0:
            self.summary_label.setText(
                "No cabinets found."
            )
            self.materials_label.setText(
                ""
            )
            self.export_button.setEnabled(
                False
            )
        else:
            self.summary_label.setText(
                f"Cabinets: {cabinet_count}    "
                f"Parts: {total_quantity}    "
                f"Board area: {total_area:.3f} m²    "
                f"Edge band: {total_edge:.2f} m"
            )

            self.materials_label.setText(
                "Materials: "
                + self._material_summary(
                    raw_rows
                )
            )

            self.export_button.setEnabled(
                bool(
                    rows
                )
            )

    def export_csv(
        self,
    ):
        if not self.display_rows:
            return

        path, _filter = QtWidgets.QFileDialog.getSaveFileName(
            Gui.getMainWindow(),
            "Export Cut List",
            "OpenInteriorCAD_CutList.csv",
            "CSV files (*.csv)",
        )

        if not path:
            return

        if not path.lower().endswith(
            ".csv"
        ):
            path += ".csv"

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
                        "Edge pattern",
                        "Edge material",
                        "Edge thickness [mm]",
                        "Edge length [m]",
                        "Area [m2]",
                    ]
                )

                for row in self.display_rows:
                    writer.writerow(
                        [
                            row["cabinet"],
                            row["part"],
                            row["role"],
                            row["quantity"],
                            f'{row["length"]:.1f}',
                            f'{row["width"]:.1f}',
                            f'{row["thickness"]:.1f}',
                            row["material"],
                            self._edge_mark(
                                row["edge_front"]
                            ),
                            self._edge_mark(
                                row["edge_back"]
                            ),
                            self._edge_mark(
                                row["edge_left"]
                            ),
                            self._edge_mark(
                                row["edge_right"]
                            ),
                            row["edge_pattern"],
                            row["edge_material"],
                            (
                                f'{row["edge_thickness"]:.1f}'
                                if row["edge_material"]
                                else ""
                            ),
                            (
                                f'{row["edge_length"]:.3f}'
                                if row["edge_material"]
                                else ""
                            ),
                            f'{row["area"]:.4f}',
                        ]
                    )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Cut List",
                f"Could not export CSV:\n{error}",
            )
            return

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Cut List",
            f"CSV exported successfully:\n{path}",
        )

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
