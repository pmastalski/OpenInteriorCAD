"""Edit panel for Cabinet Run."""

import FreeCADGui as Gui
from PySide import QtWidgets

from OICCabinetRun import (
    align_fronts, arrange_cabinets, ensure_run_properties,
    get_run_cabinets, update_run_properties,
)


class CabinetRunEditPanel:
    def __init__(self, run):
        self.run = run
        ensure_run_properties(run)

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Edit Cabinet Run")
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self.form)
        layout.addWidget(QtWidgets.QLabel("<b>OpenInteriorCAD</b><br>Edit Cabinet Run"))

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        group = QtWidgets.QGroupBox("Layout")
        group_layout = QtWidgets.QVBoxLayout(group)

        form = QtWidgets.QFormLayout()
        self.gap_input = QtWidgets.QDoubleSpinBox()
        self.gap_input.setRange(0.0, 1000.0)
        self.gap_input.setDecimals(1)
        self.gap_input.setSuffix(" mm")
        form.addRow("Cabinet Gap:", self.gap_input)
        group_layout.addLayout(form)

        row = QtWidgets.QHBoxLayout()
        self.left_button = QtWidgets.QPushButton("← Arrange")
        self.right_button = QtWidgets.QPushButton("Arrange →")
        row.addWidget(self.left_button)
        row.addWidget(self.right_button)
        group_layout.addLayout(row)

        self.align_button = QtWidgets.QPushButton("Align Fronts")
        group_layout.addWidget(self.align_button)
        layout.addWidget(group)

        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        close_button = QtWidgets.QPushButton("Close")
        layout.addWidget(close_button)
        layout.addStretch()

        self.left_button.clicked.connect(self._arrange_left)
        self.right_button.clicked.connect(self._arrange_right)
        self.align_button.clicked.connect(self._align_fronts)
        close_button.clicked.connect(Gui.Control.closeDialog)

    def _refresh(self):
        update_run_properties(self.run)
        self.gap_input.setValue(self.run.CabinetGap.Value)
        self.info_label.setText(
            f"<b>{self.run.Label}</b><br>"
            f"Cabinets: {len(get_run_cabinets(self.run))}<br>"
            f"Total Width: {self.run.TotalWidth.Value:.1f} mm"
        )
        try:
            Gui.activeDocument().activeView().redraw()
        except Exception:
            pass

    def _do(self, transaction_name, fn, message):
        doc = self.run.Document
        doc.openTransaction(transaction_name)
        try:
            fn()
            doc.recompute()
            doc.commitTransaction()
            self.status_label.setText(message)
            self._refresh()
        except Exception as error:
            doc.abortTransaction()
            self.status_label.setText(f"Error: {error}")

    def _arrange_right(self):
        gap = self.gap_input.value()
        self._do(
            "Arrange Cabinet Run Right",
            lambda: arrange_cabinets(self.run, "right", gap),
            "Cabinets arranged left to right.",
        )

    def _arrange_left(self):
        gap = self.gap_input.value()
        self._do(
            "Arrange Cabinet Run Left",
            lambda: arrange_cabinets(self.run, "left", gap),
            "Cabinets arranged right to left.",
        )

    def _align_fronts(self):
        self._do(
            "Align Cabinet Run Fronts",
            lambda: align_fronts(self.run),
            "Cabinet fronts aligned.",
        )

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True
