"""Precise movement panel for a Cabinet Run."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets
from OICCabinetRun import get_run_cabinets, move_cabinet_run


class CabinetRunMovePanel:
    def __init__(self, run):
        self.run = run
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Move Cabinet Run")
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self.form)
        self.info = QtWidgets.QLabel(
            f"<b>{self.run.Label}</b><br>"
            f"Cabinets: {len(get_run_cabinets(self.run))}"
        )
        layout.addWidget(self.info)

        self.step = QtWidgets.QDoubleSpinBox()
        self.step.setRange(0.1, 10000.0)
        self.step.setValue(10.0)
        self.step.setSuffix(" mm")
        layout.addWidget(self.step)

        grid = QtWidgets.QGridLayout()
        buttons = {
            "↑ Y+": (0, 1, 0, 1),
            "← X-": (1, 0, -1, 0),
            "X+ →": (1, 2, 1, 0),
            "↓ Y-": (2, 1, 0, -1),
        }
        for text, (r, c, dx, dy) in buttons.items():
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(lambda checked=False, x=dx, y=dy: self._move(x, y))
            grid.addWidget(b, r, c)
        layout.addLayout(grid)

        close = QtWidgets.QPushButton("Close")
        close.clicked.connect(Gui.Control.closeDialog)
        layout.addWidget(close)

    def _move(self, dx, dy):
        value = self.step.value()
        delta = App.Vector(dx * value, dy * value, 0.0)
        doc = self.run.Document
        doc.openTransaction("Move Cabinet Run")
        try:
            move_cabinet_run(self.run, delta)
            doc.commitTransaction()
        except Exception:
            doc.abortTransaction()
            raise

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True
