"""Precise movement panel for a Cabinet Run."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICCabinetRun import (
    get_run_cabinets,
    move_cabinet_run,
)


class CabinetRunMovePanel:
    """Move all cabinets in a run together."""

    def __init__(self, run):
        self.run = run
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Move Cabinet Run"
        )

        self._build_ui()
        self._refresh_info()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Move Cabinet Run"
        )

        layout.addWidget(
            title
        )

        self.info_label = QtWidgets.QLabel(
            ""
        )

        self.info_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.info_label
        )

        step_group = QtWidgets.QGroupBox(
            "Nudge"
        )

        step_layout = QtWidgets.QVBoxLayout(
            step_group
        )

        form = QtWidgets.QFormLayout()

        self.step_input = QtWidgets.QDoubleSpinBox()
        self.step_input.setRange(
            0.1,
            10000.0,
        )
        self.step_input.setDecimals(
            1
        )
        self.step_input.setValue(
            10.0
        )
        self.step_input.setSuffix(
            " mm"
        )

        form.addRow(
            "Step:",
            self.step_input,
        )

        step_layout.addLayout(
            form
        )

        grid = QtWidgets.QGridLayout()

        self.up_button = QtWidgets.QPushButton(
            "↑ Y+"
        )
        self.left_button = QtWidgets.QPushButton(
            "← X-"
        )
        self.right_button = QtWidgets.QPushButton(
            "X+ →"
        )
        self.down_button = QtWidgets.QPushButton(
            "↓ Y-"
        )

        grid.addWidget(
            self.up_button,
            0,
            1,
        )
        grid.addWidget(
            self.left_button,
            1,
            0,
        )
        grid.addWidget(
            self.right_button,
            1,
            2,
        )
        grid.addWidget(
            self.down_button,
            2,
            1,
        )

        step_layout.addLayout(
            grid
        )

        quick = QtWidgets.QHBoxLayout()

        for value in (
            1,
            5,
            10,
            50,
            100,
        ):
            button = QtWidgets.QPushButton(
                str(value)
            )
            button.clicked.connect(
                lambda checked=False, v=value:
                self.step_input.setValue(v)
            )
            quick.addWidget(
                button
            )

        step_layout.addLayout(
            quick
        )

        layout.addWidget(
            step_group
        )

        self.close_button = QtWidgets.QPushButton(
            "Close"
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        self.left_button.clicked.connect(
            lambda: self._move(
                -1.0,
                0.0,
            )
        )
        self.right_button.clicked.connect(
            lambda: self._move(
                1.0,
                0.0,
            )
        )
        self.up_button.clicked.connect(
            lambda: self._move(
                0.0,
                1.0,
            )
        )
        self.down_button.clicked.connect(
            lambda: self._move(
                0.0,
                -1.0,
            )
        )
        self.close_button.clicked.connect(
            self._close
        )

    def _refresh_info(self):
        cabinets = get_run_cabinets(
            self.run
        )

        self.info_label.setText(
            f"<b>{self.run.Label}</b><br>"
            f"Cabinets: {len(cabinets)}"
        )

    def _move(
        self,
        dx,
        dy,
    ):
        step = self.step_input.value()

        delta = App.Vector(
            dx * step,
            dy * step,
            0.0,
        )

        document = self.run.Document

        document.openTransaction(
            "Move Cabinet Run"
        )

        try:
            move_cabinet_run(
                self.run,
                delta,
            )

            document.commitTransaction()

        except Exception:
            document.abortTransaction()
            raise

        try:
            Gui.activeDocument().activeView().redraw()
        except Exception:
            pass

        self._refresh_info()

    def _close(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True
