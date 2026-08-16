"""Hardware library + assignment panel for OpenInteriorCAD.

Hardware 0.2:
- persistent hardware library,
- manufacturer / code / price,
- hardware presets,
- automatic quantity calculation,
- per-row manual quantity override,
- per-cabinet hardware selection,
- hardware cost summary.
"""

from __future__ import annotations

import csv

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from OICHardware import (
    HARDWARE_KEY_TO_TYPE,
    calculate_hardware,
    load_hardware_selection,
    reset_hardware_overrides,
    save_hardware_selection,
    save_overrides,
)
from OICHardwareLibrary import (
    HARDWARE_TYPES,
    TYPE_TO_KEY,
    display_name,
    items_of_type,
    load_library,
    load_presets,
    new_item,
    reset_library,
    reset_presets,
    save_library,
    save_presets,
)


class HardwarePanel:
    """Hardware production panel for one cabinet."""

    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture

        self.library = load_library()
        self.presets = load_presets()

        self.rows = []

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Hardware"
        )

        root = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            f"Cabinet: {getattr(furniture, 'Label', 'Cabinet')}"
        )
        title.setWordWrap(
            True
        )
        root.addWidget(
            title
        )

        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(
            self.tabs
        )

        self._build_assignment_tab()
        self._build_library_tab()

        self.refresh_assignment()
        self.populate_library_table()
        self.populate_presets()

    # ======================================================
    # UI BUILD
    # ======================================================

    def _build_assignment_tab(
        self,
    ):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(
            page
        )

        info = QtWidgets.QLabel(
            "The program calculates quantities automatically. "
            "Choose the exact hardware model from your library and optionally "
            "override only the quantity that differs from the automatic rule."
        )
        info.setWordWrap(
            True
        )
        layout.addWidget(
            info
        )

        preset_row = QtWidgets.QHBoxLayout()

        preset_row.addWidget(
            QtWidgets.QLabel(
                "Hardware preset:"
            )
        )

        self.preset_combo = QtWidgets.QComboBox()
        preset_row.addWidget(
            self.preset_combo,
            1,
        )

        self.load_preset_button = QtWidgets.QPushButton(
            "Load Preset"
        )
        self.load_preset_button.clicked.connect(
            self.load_selected_preset
        )
        preset_row.addWidget(
            self.load_preset_button
        )

        self.save_preset_button = QtWidgets.QPushButton(
            "Save Current as Preset"
        )
        self.save_preset_button.clicked.connect(
            self.save_current_preset
        )
        preset_row.addWidget(
            self.save_preset_button
        )

        layout.addLayout(
            preset_row
        )

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(
            11
        )
        self.table.setHorizontalHeaderLabels(
            [
                "Category",
                "Type",
                "Hardware",
                "Manufacturer",
                "Code",
                "Auto Qty",
                "Override",
                "Final Qty",
                "Unit",
                "Unit Price",
                "Total",
            ]
        )
        self.table.setAlternatingRowColors(
            True
        )
        self.table.verticalHeader().setVisible(
            False
        )
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )

        layout.addWidget(
            self.table
        )

        self.summary = QtWidgets.QLabel()
        self.summary.setWordWrap(
            True
        )
        layout.addWidget(
            self.summary
        )

        button_row = QtWidgets.QHBoxLayout()

        self.apply_button = QtWidgets.QPushButton(
            "Apply"
        )
        self.apply_button.clicked.connect(
            self.apply_assignment
        )
        button_row.addWidget(
            self.apply_button
        )

        self.reset_button = QtWidgets.QPushButton(
            "Reset Quantities to Automatic"
        )
        self.reset_button.clicked.connect(
            self.reset_quantities
        )
        button_row.addWidget(
            self.reset_button
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

        self.tabs.addTab(
            page,
            "Cabinet Hardware",
        )

    def _build_library_tab(
        self,
    ):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(
            page
        )

        info = QtWidgets.QLabel(
            "Hardware Library is global for OpenInteriorCAD and is stored "
            "in FreeCAD preferences."
        )
        info.setWordWrap(
            True
        )
        layout.addWidget(
            info
        )

        self.library_table = QtWidgets.QTableWidget()
        self.library_table.setColumnCount(
            8
        )
        self.library_table.setHorizontalHeaderLabels(
            [
                "Type",
                "Manufacturer",
                "Code",
                "Name",
                "Unit",
                "Unit Price",
                "Notes",
                "ID",
            ]
        )
        self.library_table.setAlternatingRowColors(
            True
        )
        self.library_table.verticalHeader().setVisible(
            False
        )
        self.library_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.library_table.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )

        layout.addWidget(
            self.library_table
        )

        buttons = QtWidgets.QHBoxLayout()

        self.add_library_button = QtWidgets.QPushButton(
            "Add"
        )
        self.add_library_button.clicked.connect(
            self.add_library_item
        )
        buttons.addWidget(
            self.add_library_button
        )

        self.delete_library_button = QtWidgets.QPushButton(
            "Delete"
        )
        self.delete_library_button.clicked.connect(
            self.delete_library_item
        )
        buttons.addWidget(
            self.delete_library_button
        )

        self.save_library_button = QtWidgets.QPushButton(
            "Save Library"
        )
        self.save_library_button.clicked.connect(
            self.save_hardware_library
        )
        buttons.addWidget(
            self.save_library_button
        )

        self.reset_library_button = QtWidgets.QPushButton(
            "Reset Defaults"
        )
        self.reset_library_button.clicked.connect(
            self.reset_hardware_library
        )
        buttons.addWidget(
            self.reset_library_button
        )

        self.delete_preset_button = QtWidgets.QPushButton(
            "Delete Current Preset"
        )
        self.delete_preset_button.clicked.connect(
            self.delete_current_preset
        )
        buttons.addWidget(
            self.delete_preset_button
        )

        self.reset_presets_button = QtWidgets.QPushButton(
            "Reset Presets"
        )
        self.reset_presets_button.clicked.connect(
            self.reset_hardware_presets
        )
        buttons.addWidget(
            self.reset_presets_button
        )

        buttons.addStretch(
            1
        )

        layout.addLayout(
            buttons
        )

        self.tabs.addTab(
            page,
            "Hardware Library",
        )

    # ======================================================
    # ASSIGNMENT TABLE
    # ======================================================

    def _read_only_item(
        self,
        value,
        align_right=False,
    ):
        item = QtWidgets.QTableWidgetItem(
            str(
                value
            )
        )
        item.setFlags(
            item.flags()
            & ~QtCore.Qt.ItemIsEditable
        )

        if align_right:
            item.setTextAlignment(
                QtCore.Qt.AlignRight
                | QtCore.Qt.AlignVCenter
            )

        return item

    def _hardware_combo(
        self,
        hardware_type,
        selected_id,
    ):
        combo = QtWidgets.QComboBox()

        items = items_of_type(
            self.library,
            hardware_type,
        )

        selected_index = -1

        for index, item in enumerate(
            items
        ):
            combo.addItem(
                display_name(
                    item
                ),
                item,
            )

            if str(
                item[
                    "id"
                ]
            ) == str(
                selected_id
            ):
                selected_index = index

        if selected_index >= 0:
            combo.setCurrentIndex(
                selected_index
            )

        return combo

    def refresh_assignment(
        self,
    ):
        rows = calculate_hardware(
            self.furniture
        )

        self.rows = []

        self.table.setRowCount(
            len(
                rows
            )
        )

        total_cost = 0.0
        total_quantity = 0

        for row_index, row in enumerate(
            rows
        ):
            hardware_type = HARDWARE_KEY_TO_TYPE.get(
                row[
                    "key"
                ],
                "",
            )

            self.table.setItem(
                row_index,
                0,
                self._read_only_item(
                    row[
                        "category"
                    ]
                ),
            )

            self.table.setItem(
                row_index,
                1,
                self._read_only_item(
                    hardware_type
                ),
            )

            combo = self._hardware_combo(
                hardware_type,
                row.get(
                    "library_id",
                    "",
                ),
            )

            self.table.setCellWidget(
                row_index,
                2,
                combo,
            )

            manufacturer_item = self._read_only_item(
                row.get(
                    "manufacturer",
                    "",
                )
            )
            code_item = self._read_only_item(
                row.get(
                    "code",
                    "",
                )
            )

            self.table.setItem(
                row_index,
                3,
                manufacturer_item,
            )
            self.table.setItem(
                row_index,
                4,
                code_item,
            )

            self.table.setItem(
                row_index,
                5,
                self._read_only_item(
                    row[
                        "auto_quantity"
                    ],
                    align_right=True,
                ),
            )

            override_box = QtWidgets.QCheckBox()
            override_box.setChecked(
                bool(
                    row.get(
                        "overridden",
                        False,
                    )
                )
            )

            override_cell = QtWidgets.QWidget()
            override_layout = QtWidgets.QHBoxLayout(
                override_cell
            )
            override_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )
            override_layout.setAlignment(
                QtCore.Qt.AlignCenter
            )
            override_layout.addWidget(
                override_box
            )

            self.table.setCellWidget(
                row_index,
                6,
                override_cell,
            )

            quantity_spin = QtWidgets.QSpinBox()
            quantity_spin.setRange(
                0,
                9999,
            )
            quantity_spin.setValue(
                int(
                    row[
                        "quantity"
                    ]
                )
            )
            quantity_spin.setEnabled(
                override_box.isChecked()
            )
            override_box.toggled.connect(
                quantity_spin.setEnabled
            )

            self.table.setCellWidget(
                row_index,
                7,
                quantity_spin,
            )

            self.table.setItem(
                row_index,
                8,
                self._read_only_item(
                    row[
                        "unit"
                    ]
                ),
            )

            self.table.setItem(
                row_index,
                9,
                self._read_only_item(
                    f'{row.get("unit_price", 0.0):.2f}',
                    align_right=True,
                ),
            )

            self.table.setItem(
                row_index,
                10,
                self._read_only_item(
                    f'{row.get("total_price", 0.0):.2f}',
                    align_right=True,
                ),
            )

            combo.currentIndexChanged.connect(
                lambda _index, row_index=row_index:
                    self._selection_changed(
                        row_index
                    )
            )

            self.rows.append(
                {
                    "key": row[
                        "key"
                    ],
                    "combo": combo,
                    "override": override_box,
                    "quantity": quantity_spin,
                }
            )

            total_cost += float(
                row.get(
                    "total_price",
                    0.0,
                )
            )
            total_quantity += int(
                row[
                    "quantity"
                ]
            )

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.summary.setText(
            f"Final hardware quantity: {total_quantity}    "
            f"Hardware cost: {total_cost:.2f}"
        )

    def _selection_changed(
        self,
        row_index,
    ):
        if (
            row_index < 0
            or row_index >= len(
                self.rows
            )
        ):
            return

        combo = self.rows[
            row_index
        ][
            "combo"
        ]

        item = combo.currentData()

        if not isinstance(
            item,
            dict,
        ):
            return

        self.table.item(
            row_index,
            3,
        ).setText(
            item.get(
                "manufacturer",
                "",
            )
        )

        self.table.item(
            row_index,
            4,
        ).setText(
            item.get(
                "code",
                "",
            )
        )

        self.table.item(
            row_index,
            8,
        ).setText(
            item.get(
                "unit",
                "",
            )
        )

        self.table.item(
            row_index,
            9,
        ).setText(
            f'{float(item.get("price", 0.0)):.2f}'
        )

        quantity = self.rows[
            row_index
        ][
            "quantity"
        ].value()

        self.table.item(
            row_index,
            10,
        ).setText(
            f'{quantity * float(item.get("price", 0.0)):.2f}'
        )

    def apply_assignment(
        self,
    ):
        overrides = {}
        selection = {}

        for row in self.rows:
            if row[
                "override"
            ].isChecked():
                overrides[
                    row[
                        "key"
                    ]
                ] = row[
                    "quantity"
                ].value()

            item = row[
                "combo"
            ].currentData()

            if isinstance(
                item,
                dict,
            ):
                selection[
                    row[
                        "key"
                    ]
                ] = item[
                    "id"
                ]

        save_overrides(
            self.furniture,
            overrides,
        )

        save_hardware_selection(
            self.furniture,
            selection,
        )

        calculate_hardware(
            self.furniture
        )

        if App.ActiveDocument is not None:
            App.ActiveDocument.recompute()

        self.refresh_assignment()

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Hardware",
            "Hardware assignment saved.",
        )

    def reset_quantities(
        self,
    ):
        reset_hardware_overrides(
            self.furniture
        )

        if App.ActiveDocument is not None:
            App.ActiveDocument.recompute()

        self.refresh_assignment()

    # ======================================================
    # HARDWARE PRESETS
    # ======================================================

    def populate_presets(
        self,
    ):
        current = self.preset_combo.currentText()

        self.presets = load_presets()
        self.preset_combo.clear()

        for preset in self.presets:
            self.preset_combo.addItem(
                preset[
                    "name"
                ],
                preset,
            )

        index = self.preset_combo.findText(
            current
        )

        if index >= 0:
            self.preset_combo.setCurrentIndex(
                index
            )

    def load_selected_preset(
        self,
    ):
        preset = self.preset_combo.currentData()

        if not isinstance(
            preset,
            dict,
        ):
            return

        for row in self.rows:
            hardware_type = HARDWARE_KEY_TO_TYPE.get(
                row[
                    "key"
                ]
            )

            preset_key = TYPE_TO_KEY.get(
                hardware_type
            )

            if not preset_key:
                continue

            wanted_id = str(
                preset.get(
                    preset_key,
                    "",
                )
            )

            combo = row[
                "combo"
            ]

            for index in range(
                combo.count()
            ):
                item = combo.itemData(
                    index
                )

                if (
                    isinstance(
                        item,
                        dict,
                    )
                    and str(
                        item.get(
                            "id",
                            "",
                        )
                    )
                    == wanted_id
                ):
                    combo.setCurrentIndex(
                        index
                    )
                    break

    def save_current_preset(
        self,
    ):
        name, ok = QtWidgets.QInputDialog.getText(
            Gui.getMainWindow(),
            "Hardware Preset",
            "Preset name:",
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        preset = {
            "name": name,
        }

        for row in self.rows:
            hardware_type = HARDWARE_KEY_TO_TYPE.get(
                row[
                    "key"
                ]
            )

            preset_key = TYPE_TO_KEY.get(
                hardware_type
            )

            if not preset_key:
                continue

            item = row[
                "combo"
            ].currentData()

            if isinstance(
                item,
                dict,
            ):
                preset[
                    preset_key
                ] = item[
                    "id"
                ]

        replaced = False

        for index, existing in enumerate(
            self.presets
        ):
            if existing[
                "name"
            ] == name:
                answer = QtWidgets.QMessageBox.question(
                    Gui.getMainWindow(),
                    "Hardware Preset",
                    f'Preset "{name}" already exists. Replace it?',
                )

                if answer != QtWidgets.QMessageBox.Yes:
                    return

                self.presets[
                    index
                ] = preset
                replaced = True
                break

        if not replaced:
            self.presets.append(
                preset
            )

        save_presets(
            self.presets
        )
        self.populate_presets()

        index = self.preset_combo.findText(
            name
        )

        if index >= 0:
            self.preset_combo.setCurrentIndex(
                index
            )

    def delete_current_preset(
        self,
    ):
        name = self.preset_combo.currentText()

        if not name:
            return

        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Hardware Preset",
            f'Delete preset "{name}"?',
        )

        if answer != QtWidgets.QMessageBox.Yes:
            return

        self.presets = [
            preset
            for preset in self.presets
            if preset[
                "name"
            ] != name
        ]

        save_presets(
            self.presets
        )
        self.populate_presets()

    def reset_hardware_presets(
        self,
    ):
        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Hardware Presets",
            "Restore default hardware presets?",
        )

        if answer != QtWidgets.QMessageBox.Yes:
            return

        self.presets = reset_presets()
        self.populate_presets()

    # ======================================================
    # LIBRARY
    # ======================================================

    def _type_combo(
        self,
        hardware_type,
    ):
        combo = QtWidgets.QComboBox()
        combo.addItems(
            HARDWARE_TYPES
        )

        index = combo.findText(
            hardware_type
        )

        if index >= 0:
            combo.setCurrentIndex(
                index
            )

        return combo

    def populate_library_table(
        self,
    ):
        self.library = load_library()

        self.library_table.setRowCount(
            len(
                self.library
            )
        )

        for row_index, item in enumerate(
            self.library
        ):
            type_combo = self._type_combo(
                item[
                    "type"
                ]
            )
            type_combo.setProperty(
                "hardware_id",
                item[
                    "id"
                ],
            )

            self.library_table.setCellWidget(
                row_index,
                0,
                type_combo,
            )

            for column, key in (
                (
                    1,
                    "manufacturer",
                ),
                (
                    2,
                    "code",
                ),
                (
                    3,
                    "name",
                ),
                (
                    4,
                    "unit",
                ),
                (
                    6,
                    "notes",
                ),
            ):
                self.library_table.setItem(
                    row_index,
                    column,
                    QtWidgets.QTableWidgetItem(
                        str(
                            item.get(
                                key,
                                "",
                            )
                        )
                    ),
                )

            price = QtWidgets.QDoubleSpinBox()
            price.setRange(
                0.0,
                999999.99,
            )
            price.setDecimals(
                2
            )
            price.setValue(
                float(
                    item.get(
                        "price",
                        0.0,
                    )
                )
            )
            self.library_table.setCellWidget(
                row_index,
                5,
                price,
            )

            id_item = self._read_only_item(
                item[
                    "id"
                ]
            )
            self.library_table.setItem(
                row_index,
                7,
                id_item,
            )

        self.library_table.resizeColumnsToContents()
        self.library_table.horizontalHeader().setStretchLastSection(
            True
        )

    def _collect_library(
        self,
    ):
        items = []

        for row in range(
            self.library_table.rowCount()
        ):
            type_combo = self.library_table.cellWidget(
                row,
                0,
            )

            price = self.library_table.cellWidget(
                row,
                5,
            )

            def text(
                column,
            ):
                item = self.library_table.item(
                    row,
                    column,
                )

                return (
                    item.text().strip()
                    if item is not None
                    else ""
                )

            record = {
                "id": text(
                    7
                ),
                "type": (
                    type_combo.currentText()
                    if type_combo is not None
                    else HARDWARE_TYPES[
                        0
                    ]
                ),
                "manufacturer": text(
                    1
                ),
                "code": text(
                    2
                ),
                "name": text(
                    3
                ),
                "unit": text(
                    4
                ),
                "price": (
                    price.value()
                    if price is not None
                    else 0.0
                ),
                "notes": text(
                    6
                ),
            }

            if record[
                "name"
            ]:
                items.append(
                    record
                )

        return items

    def add_library_item(
        self,
    ):
        hardware_type = HARDWARE_TYPES[
            0
        ]

        selected = self.library_table.currentRow()

        if selected >= 0:
            combo = self.library_table.cellWidget(
                selected,
                0,
            )

            if combo is not None:
                hardware_type = combo.currentText()

        self.library = self._collect_library()
        self.library.append(
            new_item(
                hardware_type
            )
        )
        save_library(
            self.library
        )
        self.populate_library_table()
        self.refresh_assignment()

    def delete_library_item(
        self,
    ):
        row = self.library_table.currentRow()

        if row < 0:
            return

        self.library_table.removeRow(
            row
        )

    def save_hardware_library(
        self,
    ):
        self.library = self._collect_library()
        save_library(
            self.library
        )
        self.populate_library_table()
        self.refresh_assignment()

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Hardware Library",
            "Hardware library saved.",
        )

    def reset_hardware_library(
        self,
    ):
        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Hardware Library",
            "Restore default hardware library?",
        )

        if answer != QtWidgets.QMessageBox.Yes:
            return

        self.library = reset_library()
        self.populate_library_table()
        self.refresh_assignment()

    # ======================================================
    # CSV
    # ======================================================

    def export_csv(
        self,
    ):
        rows = calculate_hardware(
            self.furniture
        )

        if not rows:
            return

        path, _filter = QtWidgets.QFileDialog.getSaveFileName(
            Gui.getMainWindow(),
            "Export Hardware CSV",
            "OpenInteriorCAD_Hardware.csv",
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
                        "Manufacturer",
                        "Code",
                        "Hardware",
                        "Unit",
                        "Auto Qty",
                        "Final Qty",
                        "Unit Price",
                        "Total Price",
                        "Override",
                    ]
                )

                cabinet = str(
                    getattr(
                        self.furniture,
                        "Label",
                        "Cabinet",
                    )
                )

                for row in rows:
                    writer.writerow(
                        [
                            cabinet,
                            row[
                                "category"
                            ],
                            row.get(
                                "manufacturer",
                                "",
                            ),
                            row.get(
                                "code",
                                "",
                            ),
                            row[
                                "name"
                            ],
                            row[
                                "unit"
                            ],
                            row[
                                "auto_quantity"
                            ],
                            row[
                                "quantity"
                            ],
                            f'{row.get("unit_price", 0.0):.2f}',
                            f'{row.get("total_price", 0.0):.2f}',
                            (
                                "YES"
                                if row.get(
                                    "overridden",
                                    False,
                                )
                                else ""
                            ),
                        ]
                    )

                writer.writerow(
                    []
                )
                writer.writerow(
                    [
                        "TOTAL",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        f'{sum(row.get("total_price", 0.0) for row in rows):.2f}',
                    ]
                )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Hardware",
                f"Could not export hardware CSV:\n{error}",
            )
            return

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Hardware",
            f"Hardware CSV exported successfully:\n{path}",
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
