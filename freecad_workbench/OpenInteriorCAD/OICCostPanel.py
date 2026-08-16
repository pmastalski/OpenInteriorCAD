"""Cost Estimate panel for OpenInteriorCAD.

Costing 0.1:
- materials
- fronts
- backs
- edges
- hardware
- per-category totals
- overall project total
- CSV export
"""

from __future__ import annotations

import csv

import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from OICCosting import calculate_project_cost


class CostPanel:
    """Production cost overview for selected cabinets or whole project."""

    def __init__(
        self,
        furniture_objects=None,
    ):
        self.furniture_objects = furniture_objects
        self.rows = []
        self.totals = {}

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Cost Estimate"
        )

        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        info = QtWidgets.QLabel(
            "If one or more cabinets are selected, only those cabinets are "
            "calculated. With no cabinet selected, the whole project is calculated."
        )
        info.setWordWrap(
            True
        )
        layout.addWidget(
            info
        )

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(
            8
        )
        self.table.setHorizontalHeaderLabels(
            [
                "Cabinet",
                "Category",
                "Item",
                "Detail",
                "Quantity",
                "Unit",
                "Unit Price",
                "Cost",
            ]
        )
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
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

        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(
            True
        )
        self.summary.setMaximumHeight(
            150
        )
        layout.addWidget(
            self.summary
        )

        buttons = QtWidgets.QHBoxLayout()

        refresh_button = QtWidgets.QPushButton(
            "Refresh"
        )
        refresh_button.clicked.connect(
            self.refresh
        )
        buttons.addWidget(
            refresh_button
        )

        export_button = QtWidgets.QPushButton(
            "Export CSV"
        )
        export_button.clicked.connect(
            self.export_csv
        )
        buttons.addWidget(
            export_button
        )

        buttons.addStretch(
            1
        )

        layout.addLayout(
            buttons
        )

        self.refresh()

    def _right_item(
        self,
        value,
    ):
        item = QtWidgets.QTableWidgetItem(
            str(
                value
            )
        )
        item.setTextAlignment(
            QtCore.Qt.AlignRight
            | QtCore.Qt.AlignVCenter
        )
        return item

    def refresh(
        self,
    ):
        self.rows, self.totals = calculate_project_cost(
            self.furniture_objects
        )

        self.table.setRowCount(
            len(
                self.rows
            )
        )

        for row_index, row in enumerate(
            self.rows
        ):
            values = [
                row[
                    "cabinet"
                ],
                row[
                    "category"
                ],
                row[
                    "item"
                ],
                row[
                    "detail"
                ],
            ]

            for column, value in enumerate(
                values
            ):
                self.table.setItem(
                    row_index,
                    column,
                    QtWidgets.QTableWidgetItem(
                        str(
                            value
                        )
                    ),
                )

            quantity = row[
                "quantity"
            ]

            if isinstance(
                quantity,
                float,
            ):
                quantity_text = f"{quantity:.3f}"
            else:
                quantity_text = str(
                    quantity
                )

            self.table.setItem(
                row_index,
                4,
                self._right_item(
                    quantity_text
                ),
            )
            self.table.setItem(
                row_index,
                5,
                QtWidgets.QTableWidgetItem(
                    row[
                        "unit"
                    ]
                ),
            )
            self.table.setItem(
                row_index,
                6,
                self._right_item(
                    f'{row["unit_price"]:.2f}'
                ),
            )
            self.table.setItem(
                row_index,
                7,
                self._right_item(
                    f'{row["cost"]:.2f}'
                ),
            )

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        order = [
            "Carcass",
            "Fronts",
            "Backs",
            "Edges",
            "Hardware",
        ]

        lines = []

        for category in order:
            lines.append(
                f"{category}: {self.totals.get(category, 0.0):.2f}"
            )

        lines.append(
            ""
        )
        lines.append(
            f"TOTAL: {self.totals.get('Total', 0.0):.2f}"
        )

        self.summary.setPlainText(
            "\n".join(
                lines
            )
        )

    def export_csv(
        self,
    ):
        if not self.rows:
            return

        path, _filter = QtWidgets.QFileDialog.getSaveFileName(
            Gui.getMainWindow(),
            "Export Cost Estimate",
            "OpenInteriorCAD_Cost_Estimate.csv",
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
                        "Category",
                        "Item",
                        "Detail",
                        "Quantity",
                        "Unit",
                        "Unit Price",
                        "Cost",
                    ]
                )

                for row in self.rows:
                    writer.writerow(
                        [
                            row[
                                "cabinet"
                            ],
                            row[
                                "category"
                            ],
                            row[
                                "item"
                            ],
                            row[
                                "detail"
                            ],
                            row[
                                "quantity"
                            ],
                            row[
                                "unit"
                            ],
                            f'{row["unit_price"]:.2f}',
                            f'{row["cost"]:.2f}',
                        ]
                    )

                writer.writerow(
                    []
                )
                writer.writerow(
                    [
                        "SUMMARY"
                    ]
                )

                for category in (
                    "Carcass",
                    "Fronts",
                    "Backs",
                    "Edges",
                    "Hardware",
                ):
                    writer.writerow(
                        [
                            category,
                            f'{self.totals.get(category, 0.0):.2f}',
                        ]
                    )

                writer.writerow(
                    [
                        "TOTAL",
                        f'{self.totals.get("Total", 0.0):.2f}',
                    ]
                )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Cost Estimate",
                f"Could not export CSV:\n{error}",
            )
            return

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Cost Estimate",
            f"Cost estimate exported successfully:\n{path}",
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
