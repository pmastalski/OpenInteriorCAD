"""Material Library panel for OpenInteriorCAD.

Materials 0.4:
- persistent material library,
- persistent material presets,
- optional thickness-to-geometry,
- color-coded material types,
- 3D hover preview showing what Carcass / Front / Back / Edge refers to.
"""

from __future__ import annotations

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from OICMaterialLibrary import (
    MATERIAL_TYPES,
    TYPE_BACK,
    TYPE_BOARD,
    TYPE_EDGE,
    TYPE_FRONT,
    display_name,
    load_materials,
    load_presets,
    material_value,
    materials_of_type,
    new_material,
    reset_materials,
    reset_presets,
    save_materials,
    save_presets,
)
from OICMaterialPreview import (
    CATEGORY_BACK,
    CATEGORY_CARCASS,
    CATEGORY_EDGE,
    CATEGORY_FRONT,
    MaterialPreview,
)


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"

TYPE_COLORS = {
    TYPE_BOARD: "#2F80ED",
    TYPE_FRONT: "#35B95F",
    TYPE_BACK: "#9B51E0",
    TYPE_EDGE: "#F26A21",
}

TYPE_CATEGORIES = {
    TYPE_BOARD: CATEGORY_CARCASS,
    TYPE_FRONT: CATEGORY_FRONT,
    TYPE_BACK: CATEGORY_BACK,
    TYPE_EDGE: CATEGORY_EDGE,
}


def selected_furniture():
    selection = Gui.Selection.getSelection()

    if len(
        selection
    ) != 1:
        return None

    obj = selection[
        0
    ]

    if getattr(
        obj,
        "OICType",
        "",
    ) != FURNITURE_TYPE:
        return None

    return obj


class HoverComboBox(
    QtWidgets.QComboBox
):
    entered = QtCore.Signal()
    left = QtCore.Signal()

    def enterEvent(
        self,
        event,
    ):
        self.entered.emit()
        super().enterEvent(
            event
        )

    def leaveEvent(
        self,
        event,
    ):
        self.left.emit()
        super().leaveEvent(
            event
        )


class HoverLabel(
    QtWidgets.QLabel
):
    entered = QtCore.Signal()
    left = QtCore.Signal()

    def enterEvent(
        self,
        event,
    ):
        self.entered.emit()
        super().enterEvent(
            event
        )

    def leaveEvent(
        self,
        event,
    ):
        self.left.emit()
        super().leaveEvent(
            event
        )


class HoverMaterialTable(
    QtWidgets.QTableWidget
):
    mouseLeft = QtCore.Signal()

    def leaveEvent(
        self,
        event,
    ):
        self.mouseLeft.emit()
        super().leaveEvent(
            event
        )


class MaterialLibraryPanel:
    """Persistent materials with color-coded 3D hover preview."""

    def __init__(
        self,
        furniture=None,
    ):
        self.furniture = (
            furniture
            if furniture is not None
            else selected_furniture()
        )

        self.records = load_materials()
        self.presets = load_presets()

        self.preview = MaterialPreview()

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Material Library"
        )

        root = QtWidgets.QVBoxLayout(
            self.form
        )

        # --------------------------------------------------
        # LEGEND
        # --------------------------------------------------

        legend_group = QtWidgets.QGroupBox(
            "Material Types"
        )

        legend_layout = QtWidgets.QHBoxLayout(
            legend_group
        )

        self._legend_item(
            legend_layout,
            TYPE_BOARD,
            "Carcass",
        )
        self._legend_item(
            legend_layout,
            TYPE_FRONT,
            "Front",
        )
        self._legend_item(
            legend_layout,
            TYPE_BACK,
            "Back",
        )
        self._legend_item(
            legend_layout,
            TYPE_EDGE,
            "Edge",
        )

        legend_layout.addStretch(
            1
        )

        root.addWidget(
            legend_group
        )

        hover_info = QtWidgets.QLabel(
            "Hover over a material row, assignment label or material selector "
            "to highlight the corresponding parts directly on the cabinet."
        )
        hover_info.setWordWrap(
            True
        )
        root.addWidget(
            hover_info
        )

        # --------------------------------------------------
        # LIBRARY
        # --------------------------------------------------

        library_group = QtWidgets.QGroupBox(
            "Material Library"
        )

        library_layout = QtWidgets.QVBoxLayout(
            library_group
        )

        self.table = HoverMaterialTable()
        self.table.setColumnCount(
            5
        )
        self.table.setHorizontalHeaderLabels(
            [
                "Type",
                "Manufacturer",
                "Code",
                "Name",
                "Thickness",
            ]
        )
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.table.setAlternatingRowColors(
            True
        )
        self.table.verticalHeader().setVisible(
            False
        )
        self.table.setMouseTracking(
            True
        )
        self.table.viewport().setMouseTracking(
            True
        )
        self.table.cellEntered.connect(
            self._library_cell_entered
        )
        self.table.mouseLeft.connect(
            self._clear_preview
        )

        library_layout.addWidget(
            self.table
        )

        buttons = QtWidgets.QHBoxLayout()

        self.add_button = QtWidgets.QPushButton(
            "Add"
        )
        self.add_button.clicked.connect(
            self.add_material
        )
        buttons.addWidget(
            self.add_button
        )

        self.delete_button = QtWidgets.QPushButton(
            "Delete"
        )
        self.delete_button.clicked.connect(
            self.delete_material
        )
        buttons.addWidget(
            self.delete_button
        )

        self.save_button = QtWidgets.QPushButton(
            "Save Library"
        )
        self.save_button.clicked.connect(
            self.save_library
        )
        buttons.addWidget(
            self.save_button
        )

        self.reset_button = QtWidgets.QPushButton(
            "Reset Defaults"
        )
        self.reset_button.clicked.connect(
            self.reset_library
        )
        buttons.addWidget(
            self.reset_button
        )

        buttons.addStretch(
            1
        )
        library_layout.addLayout(
            buttons
        )

        root.addWidget(
            library_group
        )

        # --------------------------------------------------
        # PRESETS
        # --------------------------------------------------

        preset_group = QtWidgets.QGroupBox(
            "Material Presets"
        )
        preset_layout = QtWidgets.QGridLayout(
            preset_group
        )

        self.preset_combo = QtWidgets.QComboBox()

        preset_layout.addWidget(
            QtWidgets.QLabel(
                "Preset:"
            ),
            0,
            0,
        )
        preset_layout.addWidget(
            self.preset_combo,
            0,
            1,
            1,
            3,
        )

        self.apply_preset_button = QtWidgets.QPushButton(
            "Load Preset"
        )
        self.apply_preset_button.clicked.connect(
            self.load_selected_preset
        )
        preset_layout.addWidget(
            self.apply_preset_button,
            1,
            0,
        )

        self.save_preset_button = QtWidgets.QPushButton(
            "Save Current as Preset"
        )
        self.save_preset_button.clicked.connect(
            self.save_current_preset
        )
        preset_layout.addWidget(
            self.save_preset_button,
            1,
            1,
        )

        self.delete_preset_button = QtWidgets.QPushButton(
            "Delete Preset"
        )
        self.delete_preset_button.clicked.connect(
            self.delete_preset
        )
        preset_layout.addWidget(
            self.delete_preset_button,
            1,
            2,
        )

        self.reset_presets_button = QtWidgets.QPushButton(
            "Reset Presets"
        )
        self.reset_presets_button.clicked.connect(
            self.reset_preset_library
        )
        preset_layout.addWidget(
            self.reset_presets_button,
            1,
            3,
        )

        root.addWidget(
            preset_group
        )

        # --------------------------------------------------
        # CABINET ASSIGNMENT
        # --------------------------------------------------

        assignment_group = QtWidgets.QGroupBox(
            "Selected Cabinet"
        )
        assignment_layout = QtWidgets.QFormLayout(
            assignment_group
        )

        self.cabinet_label = QtWidgets.QLabel()
        assignment_layout.addRow(
            "Cabinet:",
            self.cabinet_label,
        )

        self.board_combo = HoverComboBox()
        self.front_combo = HoverComboBox()
        self.back_combo = HoverComboBox()
        self.edge_combo = HoverComboBox()

        self._add_assignment_row(
            assignment_layout,
            "Carcass:",
            self.board_combo,
            TYPE_BOARD,
        )

        self._add_assignment_row(
            assignment_layout,
            "Front:",
            self.front_combo,
            TYPE_FRONT,
        )

        self._add_assignment_row(
            assignment_layout,
            "Back:",
            self.back_combo,
            TYPE_BACK,
        )

        self._add_assignment_row(
            assignment_layout,
            "Edge band:",
            self.edge_combo,
            TYPE_EDGE,
        )

        self.edge_thickness = QtWidgets.QDoubleSpinBox()
        self.edge_thickness.setRange(
            0.1,
            10.0,
        )
        self.edge_thickness.setDecimals(
            2
        )
        self.edge_thickness.setSuffix(
            " mm"
        )
        assignment_layout.addRow(
            "Edge thickness:",
            self.edge_thickness,
        )

        self.apply_geometry_thickness = QtWidgets.QCheckBox(
            "Apply material thickness to geometry"
        )
        self.apply_geometry_thickness.setChecked(
            False
        )
        self.apply_geometry_thickness.setToolTip(
            "Board -> PanelThickness, Front -> FrontThickness, "
            "Back -> BackThickness."
        )
        assignment_layout.addRow(
            self.apply_geometry_thickness
        )

        self.geometry_warning = QtWidgets.QLabel(
            "Geometry thickness changes only when the checkbox above is enabled."
        )
        self.geometry_warning.setWordWrap(
            True
        )
        assignment_layout.addRow(
            self.geometry_warning
        )

        self.apply_button = QtWidgets.QPushButton(
            "Apply to Cabinet"
        )
        self.apply_button.clicked.connect(
            self.apply_to_cabinet
        )
        assignment_layout.addRow(
            self.apply_button
        )

        root.addWidget(
            assignment_group
        )

        self._populate_table()
        self._populate_assignment()
        self._populate_presets()

    # ======================================================
    # COLOR / HOVER
    # ======================================================

    def _color_style(
        self,
        material_type,
    ):
        color = TYPE_COLORS.get(
            material_type,
            "#808080",
        )

        return (
            "QLabel {"
            f"background-color: {color};"
            "border-radius: 5px;"
            "min-width: 12px;"
            "max-width: 12px;"
            "min-height: 12px;"
            "max-height: 12px;"
            "}"
        )

    def _legend_item(
        self,
        layout,
        material_type,
        text,
    ):
        dot = HoverLabel()
        dot.setStyleSheet(
            self._color_style(
                material_type
            )
        )

        label = HoverLabel(
            text
        )

        category = TYPE_CATEGORIES[
            material_type
        ]

        for widget in (
            dot,
            label,
        ):
            widget.entered.connect(
                lambda category=category:
                    self._show_preview(
                        category
                    )
            )
            widget.left.connect(
                self._clear_preview
            )

        layout.addWidget(
            dot
        )
        layout.addWidget(
            label
        )

    def _add_assignment_row(
        self,
        form_layout,
        text,
        combo,
        material_type,
    ):
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(
            row_widget
        )
        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        dot = HoverLabel()
        dot.setStyleSheet(
            self._color_style(
                material_type
            )
        )

        text_label = HoverLabel(
            text
        )

        row_layout.addWidget(
            dot
        )
        row_layout.addWidget(
            text_label
        )
        row_layout.addStretch(
            1
        )

        category = TYPE_CATEGORIES[
            material_type
        ]

        for widget in (
            dot,
            text_label,
            combo,
        ):
            widget.entered.connect(
                lambda category=category:
                    self._show_preview(
                        category
                    )
            )
            widget.left.connect(
                self._clear_preview
            )

        form_layout.addRow(
            row_widget,
            combo,
        )

    def _show_preview(
        self,
        category,
    ):
        if self.furniture is None:
            return

        self.preview.show(
            self.furniture,
            category,
        )

    def _clear_preview(
        self,
        *_args,
    ):
        self.preview.clear()

    def _library_cell_entered(
        self,
        row,
        _column,
    ):
        if (
            row < 0
            or row >= self.table.rowCount()
        ):
            return

        combo = self.table.cellWidget(
            row,
            0,
        )

        if combo is None:
            return

        material_type = combo.currentText()

        category = TYPE_CATEGORIES.get(
            material_type
        )

        if category:
            self._show_preview(
                category
            )

    # ======================================================
    # MATERIAL TABLE
    # ======================================================

    def _type_combo(
        self,
        material_type,
    ):
        combo = QtWidgets.QComboBox()
        combo.addItems(
            MATERIAL_TYPES
        )

        index = combo.findText(
            material_type
        )

        if index >= 0:
            combo.setCurrentIndex(
                index
            )

        self._style_type_combo(
            combo
        )
        combo.currentTextChanged.connect(
            lambda _text, combo=combo:
                self._style_type_combo(
                    combo
                )
        )

        return combo

    def _style_type_combo(
        self,
        combo,
    ):
        color = TYPE_COLORS.get(
            combo.currentText(),
            "#808080",
        )

        combo.setStyleSheet(
            "QComboBox {"
            f"border-left: 6px solid {color};"
            "padding-left: 5px;"
            "}"
        )

    def _thickness_spin(
        self,
        value,
    ):
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(
            0.1,
            100.0,
        )
        spin.setDecimals(
            2
        )
        spin.setSuffix(
            " mm"
        )
        spin.setValue(
            float(
                value
            )
        )
        return spin

    def _populate_table(
        self,
    ):
        self.table.setRowCount(
            len(
                self.records
            )
        )

        for row, record in enumerate(
            self.records
        ):
            type_combo = self._type_combo(
                record[
                    "type"
                ]
            )
            type_combo.setProperty(
                "material_id",
                record[
                    "id"
                ],
            )
            self.table.setCellWidget(
                row,
                0,
                type_combo,
            )

            background = QtGui.QColor(
                TYPE_COLORS.get(
                    record[
                        "type"
                    ],
                    "#808080",
                )
            )
            background.setAlpha(
                35
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
            ):
                item = QtWidgets.QTableWidgetItem(
                    str(
                        record.get(
                            key,
                            "",
                        )
                    )
                )
                item.setBackground(
                    background
                )
                self.table.setItem(
                    row,
                    column,
                    item,
                )

            thickness = self._thickness_spin(
                record.get(
                    "thickness",
                    0.0,
                )
            )
            self.table.setCellWidget(
                row,
                4,
                thickness,
            )

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(
            True
        )

    def _collect_table(
        self,
    ):
        records = []

        for row in range(
            self.table.rowCount()
        ):
            type_combo = self.table.cellWidget(
                row,
                0,
            )
            thickness = self.table.cellWidget(
                row,
                4,
            )

            material_id = ""

            if type_combo is not None:
                material_id = str(
                    type_combo.property(
                        "material_id"
                    )
                    or ""
                )

            def cell_text(
                column,
            ):
                item = self.table.item(
                    row,
                    column,
                )
                return (
                    item.text().strip()
                    if item is not None
                    else ""
                )

            record = {
                "id": material_id,
                "type": (
                    type_combo.currentText()
                    if type_combo is not None
                    else TYPE_BOARD
                ),
                "manufacturer": cell_text(
                    1
                ),
                "code": cell_text(
                    2
                ),
                "name": cell_text(
                    3
                ),
                "thickness": (
                    thickness.value()
                    if thickness is not None
                    else 0.0
                ),
            }

            if record[
                "name"
            ]:
                records.append(
                    record
                )

        return records

    def add_material(
        self,
    ):
        material_type = TYPE_BOARD
        selected = self.table.currentRow()

        if selected >= 0:
            combo = self.table.cellWidget(
                selected,
                0,
            )
            if combo is not None:
                material_type = combo.currentText()

        self.records = self._collect_table()
        self.records.append(
            new_material(
                material_type
            )
        )
        self._populate_table()

        last_row = (
            self.table.rowCount()
            - 1
        )

        if last_row >= 0:
            self.table.selectRow(
                last_row
            )

    def delete_material(
        self,
    ):
        row = self.table.currentRow()

        if row >= 0:
            self.table.removeRow(
                row
            )

    def save_library(
        self,
    ):
        self.records = self._collect_table()
        save_materials(
            self.records
        )
        self.records = load_materials()

        self._populate_table()
        self._populate_assignment()
        self._populate_presets()

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Material Library",
            "Material library saved.",
        )

    def reset_library(
        self,
    ):
        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Material Library",
            "Restore the default material library?",
        )

        if answer != QtWidgets.QMessageBox.Yes:
            return

        self.records = reset_materials()
        self._populate_table()
        self._populate_assignment()
        self._populate_presets()

    # ======================================================
    # PRESETS
    # ======================================================

    def _populate_presets(
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

    def _selected_material_id(
        self,
        combo,
    ):
        record = self._combo_record(
            combo
        )

        if record is None:
            return ""

        return str(
            record.get(
                "id",
                "",
            )
        )

    def _set_combo_material_id(
        self,
        combo,
        material_type,
        material_id,
    ):
        records = materials_of_type(
            self.records,
            material_type,
        )

        for index, record in enumerate(
            records
        ):
            if str(
                record.get(
                    "id",
                    "",
                )
            ) == str(
                material_id
            ):
                combo.setCurrentIndex(
                    index
                )
                return True

        return False

    def load_selected_preset(
        self,
    ):
        preset = self.preset_combo.currentData()

        if not isinstance(
            preset,
            dict,
        ):
            return

        self._set_combo_material_id(
            self.board_combo,
            TYPE_BOARD,
            preset.get(
                "board_id",
                "",
            ),
        )
        self._set_combo_material_id(
            self.front_combo,
            TYPE_FRONT,
            preset.get(
                "front_id",
                "",
            ),
        )
        self._set_combo_material_id(
            self.back_combo,
            TYPE_BACK,
            preset.get(
                "back_id",
                "",
            ),
        )

        edge_changed = self._set_combo_material_id(
            self.edge_combo,
            TYPE_EDGE,
            preset.get(
                "edge_id",
                "",
            ),
        )

        if edge_changed:
            self._edge_material_changed()

    def save_current_preset(
        self,
    ):
        name, ok = QtWidgets.QInputDialog.getText(
            Gui.getMainWindow(),
            "Save Material Preset",
            "Preset name:",
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        preset = {
            "name": name,
            "board_id": self._selected_material_id(
                self.board_combo
            ),
            "front_id": self._selected_material_id(
                self.front_combo
            ),
            "back_id": self._selected_material_id(
                self.back_combo
            ),
            "edge_id": self._selected_material_id(
                self.edge_combo
            ),
        }

        replaced = False

        for index, existing in enumerate(
            self.presets
        ):
            if existing[
                "name"
            ] == name:
                answer = QtWidgets.QMessageBox.question(
                    Gui.getMainWindow(),
                    "Material Preset",
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
        self._populate_presets()

        index = self.preset_combo.findText(
            name
        )

        if index >= 0:
            self.preset_combo.setCurrentIndex(
                index
            )

    def delete_preset(
        self,
    ):
        index = self.preset_combo.currentIndex()

        if index < 0:
            return

        name = self.preset_combo.currentText()

        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Material Preset",
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
        self._populate_presets()

    def reset_preset_library(
        self,
    ):
        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Material Presets",
            "Restore the default material presets?",
        )

        if answer != QtWidgets.QMessageBox.Yes:
            return

        self.presets = reset_presets()
        self._populate_presets()

    # ======================================================
    # ASSIGNMENT
    # ======================================================

    def _fill_combo(
        self,
        combo,
        material_type,
        current_value="",
    ):
        combo.clear()

        records = materials_of_type(
            self.records,
            material_type,
        )

        current_value = str(
            current_value
        ).strip()

        best_index = -1

        for index, record in enumerate(
            records
        ):
            combo.addItem(
                display_name(
                    record
                ),
                record,
            )

            if material_value(
                record
            ) == current_value:
                best_index = index

        if best_index >= 0:
            combo.setCurrentIndex(
                best_index
            )

        color = TYPE_COLORS.get(
            material_type,
            "#808080",
        )

        combo.setStyleSheet(
            "QComboBox {"
            f"border-left: 6px solid {color};"
            "padding-left: 5px;"
            "}"
        )

    def _populate_assignment(
        self,
    ):
        furniture = self.furniture

        if furniture is None:
            self.cabinet_label.setText(
                "No single cabinet selected"
            )

            for widget in (
                self.board_combo,
                self.front_combo,
                self.back_combo,
                self.edge_combo,
                self.edge_thickness,
                self.apply_geometry_thickness,
                self.apply_button,
            ):
                widget.setEnabled(
                    False
                )

            return

        try:
            furniture.Proxy._ensure_board_part_properties(
                furniture
            )
        except Exception:
            pass

        self.cabinet_label.setText(
            str(
                getattr(
                    furniture,
                    "Label",
                    "Cabinet",
                )
            )
        )

        for widget in (
            self.board_combo,
            self.front_combo,
            self.back_combo,
            self.edge_combo,
            self.edge_thickness,
            self.apply_geometry_thickness,
            self.apply_button,
        ):
            widget.setEnabled(
                True
            )

        self._fill_combo(
            self.board_combo,
            TYPE_BOARD,
            getattr(
                furniture,
                "BoardMaterial",
                "",
            ),
        )
        self._fill_combo(
            self.front_combo,
            TYPE_FRONT,
            getattr(
                furniture,
                "FrontMaterial",
                "",
            ),
        )
        self._fill_combo(
            self.back_combo,
            TYPE_BACK,
            getattr(
                furniture,
                "BackMaterial",
                "",
            ),
        )
        self._fill_combo(
            self.edge_combo,
            TYPE_EDGE,
            getattr(
                furniture,
                "EdgeMaterial",
                "",
            ),
        )

        try:
            self.edge_thickness.setValue(
                float(
                    furniture.EdgeThickness.Value
                )
            )
        except Exception:
            self.edge_thickness.setValue(
                0.8
            )

        self.edge_combo.currentIndexChanged.connect(
            self._edge_material_changed
        )

    def _combo_record(
        self,
        combo,
    ):
        data = combo.currentData()
        return (
            data
            if isinstance(
                data,
                dict,
            )
            else None
        )

    def _edge_material_changed(
        self,
        *_args,
    ):
        record = self._combo_record(
            self.edge_combo
        )

        if record is None:
            return

        try:
            thickness = float(
                record.get(
                    "thickness",
                    0.8,
                )
            )
        except Exception:
            thickness = 0.8

        if thickness > 0.0:
            self.edge_thickness.setValue(
                thickness
            )

    # ======================================================
    # GEOMETRY THICKNESS
    # ======================================================

    def _material_thickness(
        self,
        record,
        fallback,
    ):
        if record is None:
            return float(
                fallback
            )

        try:
            return float(
                record.get(
                    "thickness",
                    fallback,
                )
            )
        except Exception:
            return float(
                fallback
            )

    def _geometry_thicknesses_are_valid(
        self,
        board_thickness,
        front_thickness,
        back_thickness,
    ):
        if (
            board_thickness <= 0.1
            or front_thickness <= 0.1
            or back_thickness <= 0.1
        ):
            return (
                False,
                "Material thickness must be greater than 0.1 mm.",
            )

        if board_thickness >= 100.0:
            return (
                False,
                "Carcass board thickness is unrealistically large.",
            )

        if front_thickness >= 100.0:
            return (
                False,
                "Front thickness is unrealistically large.",
            )

        if back_thickness >= 50.0:
            return (
                False,
                "Back thickness is unrealistically large.",
            )

        furniture = self.furniture

        cabinet_type = str(
            getattr(
                furniture,
                "CabinetType",
                "",
            )
        )

        try:
            width_a = float(
                furniture.Width.Value
            )
            depth_a = float(
                furniture.Depth.Value
            )
        except Exception:
            width_a = 0.0
            depth_a = 0.0

        if cabinet_type in {
            "Corner Base",
            "Corner Wall",
        }:
            try:
                width_b = float(
                    furniture.WidthB.Value
                )
                depth_b = float(
                    furniture.DepthB.Value
                )
            except Exception:
                width_b = 0.0
                depth_b = 0.0

            margin = (
                board_thickness
                + 0.1
            )

            if (
                width_a - depth_b <= margin
                or width_b - depth_a <= margin
            ):
                return (
                    False,
                    "The selected carcass thickness is too large for the "
                    "current corner-cabinet Width A/B and Depth A/B.",
                )
        else:
            if (
                width_a > 0.0
                and width_a
                <= 2.0 * board_thickness + 0.1
            ):
                return (
                    False,
                    "The selected carcass thickness leaves no usable internal width.",
                )

            if (
                depth_a > 0.0
                and depth_a
                <= back_thickness + 0.1
            ):
                return (
                    False,
                    "The selected back thickness is too large for the cabinet depth.",
                )

        return (
            True,
            "",
        )

    def _apply_geometry_thickness_values(
        self,
        board,
        front,
        back,
    ):
        furniture = self.furniture

        current_board = float(
            furniture.PanelThickness.Value
        )
        current_front = float(
            furniture.FrontThickness.Value
        )
        current_back = float(
            furniture.BackThickness.Value
        )

        board_thickness = self._material_thickness(
            board,
            current_board,
        )
        front_thickness = self._material_thickness(
            front,
            current_front,
        )
        back_thickness = self._material_thickness(
            back,
            current_back,
        )

        valid, message = self._geometry_thicknesses_are_valid(
            board_thickness,
            front_thickness,
            back_thickness,
        )

        if not valid:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Material Library",
                "Geometry thickness was not changed.\n\n"
                + message,
            )
            return False

        document = App.ActiveDocument

        if document is not None:
            document.openTransaction(
                "Apply Material Thickness"
            )

        try:
            furniture.PanelThickness = (
                board_thickness
            )
            furniture.FrontThickness = (
                front_thickness
            )
            furniture.BackThickness = (
                back_thickness
            )

            if document is not None:
                document.recompute()
                document.commitTransaction()

        except Exception as error:
            if document is not None:
                try:
                    document.abortTransaction()
                except Exception:
                    pass

            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Material Library",
                "Could not apply material thickness to geometry:\n"
                f"{error}",
            )
            return False

        return True

    # ======================================================
    # APPLY
    # ======================================================

    def apply_to_cabinet(
        self,
    ):
        self.preview.clear()

        furniture = self.furniture

        if furniture is None:
            return

        board = self._combo_record(
            self.board_combo
        )
        front = self._combo_record(
            self.front_combo
        )
        back = self._combo_record(
            self.back_combo
        )
        edge = self._combo_record(
            self.edge_combo
        )

        if board is not None:
            furniture.BoardMaterial = material_value(
                board
            )

        if front is not None:
            furniture.FrontMaterial = material_value(
                front
            )

        if back is not None:
            furniture.BackMaterial = material_value(
                back
            )

        if edge is not None:
            furniture.EdgeMaterial = material_value(
                edge
            )

        furniture.EdgeThickness = (
            self.edge_thickness.value()
        )

        geometry_changed = False

        if self.apply_geometry_thickness.isChecked():
            geometry_changed = self._apply_geometry_thickness_values(
                board,
                front,
                back,
            )

            if not geometry_changed:
                try:
                    furniture.Proxy._update_board_parts(
                        furniture
                    )
                except Exception:
                    pass

                if App.ActiveDocument is not None:
                    App.ActiveDocument.recompute()

                return

        try:
            furniture.Proxy._update_board_parts(
                furniture
            )
        except Exception:
            pass

        if App.ActiveDocument is not None:
            App.ActiveDocument.recompute()

        message = (
            "Materials assigned to the selected cabinet."
        )

        if geometry_changed:
            message += (
                "\n\nGeometry thickness updated:"
                f"\nPanelThickness = {float(furniture.PanelThickness.Value):g} mm"
                f"\nFrontThickness = {float(furniture.FrontThickness.Value):g} mm"
                f"\nBackThickness = {float(furniture.BackThickness.Value):g} mm"
            )

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Material Library",
            message,
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
        self.preview.clear()
        Gui.Control.closeDialog()
        return True

    def accept(
        self,
    ):
        self.preview.clear()
        Gui.Control.closeDialog()
        return True

    def __del__(
        self,
    ):
        try:
            self.preview.clear()
        except Exception:
            pass
