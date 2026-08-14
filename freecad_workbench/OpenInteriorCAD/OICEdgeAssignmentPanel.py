"""Interactive Edge Assignment panel for OpenInteriorCAD.

Cut List 0.9:
- shows current edge assignments on the model as soon as the panel opens,
- active edges = orange,
- inactive selectable edges = translucent grey,
- hover = yellow,
- edge can be toggled from the table OR directly by clicking its face in 3D.
"""

from __future__ import annotations

import json

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from OICBoardParts import build_board_parts
from OICEdgePreview import EdgePreview


class HoverCellWidget(
    QtWidgets.QWidget
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


class HoverTableWidget(
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


class EdgeAssignmentPanel:
    """Edit edge-band flags from both table and 3D model."""

    EDGE_COLUMNS = {
        3: "front",
        4: "back",
        5: "left",
        6: "right",
    }

    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture
        self.rows = []

        self._updating_ui = False

        self.preview = EdgePreview(
            on_face_clicked=self._toggle_from_model
        )

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Edge Assignment"
        )

        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            f"Cabinet: {getattr(furniture, 'Label', 'Cabinet')}"
        )

        title.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )

        info = QtWidgets.QLabel(
            "Orange = edge band ON    •    Grey = edge band OFF    •    "
            "Yellow = hovered edge. "
            "Click an edge face directly on the 3D model to switch it ON/OFF."
        )

        info.setWordWrap(
            True
        )

        layout.addWidget(
            info
        )

        self.table = HoverTableWidget()

        self.table.setColumnCount(
            7
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Part",
                "Role",
                "Qty",
                "Front",
                "Back",
                "Left",
                "Right",
            ]
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )

        self.table.setMouseTracking(
            True
        )

        self.table.viewport().setMouseTracking(
            True
        )

        self.table.cellEntered.connect(
            self._cell_entered
        )

        self.table.mouseLeft.connect(
            self._table_left
        )

        layout.addWidget(
            self.table
        )

        hint = QtWidgets.QLabel(
            "The 3D indicators are temporary Coin3D graphics only. "
            "They do not change cabinet geometry."
        )

        hint.setWordWrap(
            True
        )

        layout.addWidget(
            hint
        )

        button_row = QtWidgets.QHBoxLayout()

        self.reset_button = QtWidgets.QPushButton(
            "Reset to Automatic"
        )

        self.reset_button.clicked.connect(
            self.reset_to_automatic
        )

        button_row.addWidget(
            self.reset_button
        )

        self.apply_button = QtWidgets.QPushButton(
            "Apply"
        )

        self.apply_button.clicked.connect(
            self.apply_changes
        )

        button_row.addWidget(
            self.apply_button
        )

        button_row.addStretch(
            1
        )

        layout.addLayout(
            button_row
        )

        self.refresh()

    # ======================================================
    # ASSIGNMENT STATE
    # ======================================================

    def _current_assignments(
        self,
    ):
        assignments = {}

        for row in self.rows:
            checks = row[
                "checkboxes"
            ]

            assignments[
                row[
                    "name"
                ]
            ] = {
                "front": checks[
                    "front"
                ].isChecked(),
                "back": checks[
                    "back"
                ].isChecked(),
                "left": checks[
                    "left"
                ].isChecked(),
                "right": checks[
                    "right"
                ].isChecked(),
            }

        return assignments

    def _sync_model(
        self,
        hover_target=None,
    ):
        if not self.rows:
            self.preview.clear()
            return

        assignments = self._current_assignments()

        self.preview.show_assignments(
            self.furniture,
            assignments,
            hover_target=hover_target,
        )

    # ======================================================
    # MODEL CLICK
    # ======================================================

    def _find_row(
        self,
        part_name,
    ):
        for index, row in enumerate(
            self.rows
        ):
            if row[
                "name"
            ] == part_name:
                return index

        return None

    def _toggle_from_model(
        self,
        part_name,
        edge_name,
    ):
        row_index = self._find_row(
            part_name
        )

        if row_index is None:
            return

        row = self.rows[
            row_index
        ]

        checkbox = row[
            "checkboxes"
        ].get(
            edge_name
        )

        if checkbox is None:
            return

        self._updating_ui = True

        try:
            checkbox.setChecked(
                not checkbox.isChecked()
            )

        finally:
            self._updating_ui = False

        # Keep that edge highlighted after clicking.
        self._sync_model(
            hover_target=(
                part_name,
                edge_name,
            )
        )

    # ======================================================
    # TABLE HOVER
    # ======================================================

    def _cell_entered(
        self,
        row,
        column,
    ):
        if (
            row < 0
            or row >= len(
                self.rows
            )
        ):
            return

        part_name = self.rows[
            row
        ][
            "name"
        ]

        if column <= 2:
            self.preview.set_hover(
                part_name,
                None,
            )

            return

        edge_name = self.EDGE_COLUMNS.get(
            column
        )

        self.preview.set_hover(
            part_name,
            edge_name,
        )

    def _table_left(
        self,
    ):
        # Do not clear the persistent model indicators.
        # Only remove temporary yellow hover emphasis.
        self.preview.set_hover(
            None,
            None,
        )

    # ======================================================
    # TABLE
    # ======================================================

    def _checkbox_changed(
        self,
        *_args,
    ):
        if self._updating_ui:
            return

        self._sync_model()

    def _checkbox_cell(
        self,
        row,
        edge_name,
        checked,
    ):
        widget = HoverCellWidget()

        layout = QtWidgets.QHBoxLayout(
            widget
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setAlignment(
            QtCore.Qt.AlignCenter
        )

        box = QtWidgets.QCheckBox()

        box.setChecked(
            bool(
                checked
            )
        )

        box.toggled.connect(
            self._checkbox_changed
        )

        layout.addWidget(
            box
        )

        widget.entered.connect(
            lambda row=row, edge_name=edge_name:
                self._show_table_hover(
                    row,
                    edge_name,
                )
        )

        return widget, box

    def _show_table_hover(
        self,
        row,
        edge_name,
    ):
        if (
            row < 0
            or row >= len(
                self.rows
            )
        ):
            return

        self.preview.set_hover(
            self.rows[
                row
            ][
                "name"
            ],
            edge_name,
        )

    def refresh(
        self,
    ):
        self.preview.clear()

        parts = build_board_parts(
            self.furniture
        )

        self.rows = []

        self._updating_ui = True

        try:
            self.table.setRowCount(
                len(
                    parts
                )
            )

            for row_index, part in enumerate(
                parts
            ):
                name = str(
                    part.get(
                        "name",
                        "",
                    )
                )

                role = str(
                    part.get(
                        "role",
                        "",
                    )
                )

                qty = int(
                    part.get(
                        "quantity",
                        1,
                    )
                )

                for column, value in (
                    (
                        0,
                        name,
                    ),
                    (
                        1,
                        role,
                    ),
                    (
                        2,
                        str(
                            qty
                        ),
                    ),
                ):
                    item = QtWidgets.QTableWidgetItem(
                        value
                    )

                    item.setFlags(
                        item.flags()
                        & ~QtCore.Qt.ItemIsEditable
                    )

                    self.table.setItem(
                        row_index,
                        column,
                        item,
                    )

                checkboxes = {}

                for column, key in (
                    (
                        3,
                        "front",
                    ),
                    (
                        4,
                        "back",
                    ),
                    (
                        5,
                        "left",
                    ),
                    (
                        6,
                        "right",
                    ),
                ):
                    widget, box = self._checkbox_cell(
                        row_index,
                        key,
                        part.get(
                            f"edge_{key}",
                            False,
                        ),
                    )

                    self.table.setCellWidget(
                        row_index,
                        column,
                        widget,
                    )

                    checkboxes[
                        key
                    ] = box

                self.rows.append(
                    {
                        "name": name,
                        "checkboxes": checkboxes,
                    }
                )

        finally:
            self._updating_ui = False

        self.table.resizeColumnsToContents()

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        # This is the key 0.9 behavior:
        # show current assignments immediately when the panel opens.
        self._sync_model()

    # ======================================================
    # SAVE / RESET
    # ======================================================

    def _collect_overrides(
        self,
    ):
        return self._current_assignments()

    def apply_changes(
        self,
    ):
        overrides = self._collect_overrides()

        self.furniture.EdgeOverridesJSON = json.dumps(
            overrides,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

        try:
            self.furniture.Proxy._update_board_parts(
                self.furniture
            )

        except Exception:
            pass

        if App.ActiveDocument is not None:
            App.ActiveDocument.recompute()

        # Rebuild preview because the cabinet may have recomputed.
        self._sync_model()

        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Edge Assignment",
            "Edge assignment saved.",
        )

    def reset_to_automatic(
        self,
    ):
        self.preview.clear()

        self.furniture.EdgeOverridesJSON = "{}"

        try:
            self.furniture.Proxy._update_board_parts(
                self.furniture
            )

        except Exception:
            pass

        if App.ActiveDocument is not None:
            App.ActiveDocument.recompute()

        self.refresh()

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
        self.apply_changes()

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
