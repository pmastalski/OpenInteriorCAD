"""Task panel for snapping a Cabinet Run to a wall."""

import FreeCADGui as Gui
from PySide import QtWidgets

from OICCabinetRunSnapWall import CabinetRunSnapWallTool


class CabinetRunSnapWallPanel:
    def __init__(self, run):
        self.run = run
        self.tool = None

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Snap Run to Wall")

        layout = QtWidgets.QVBoxLayout(self.form)

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>Snap Run to Wall"
        )
        layout.addWidget(title)

        info = QtWidgets.QLabel(
            "Pick a physical wall face. The backs of all cabinets "
            "will be parallel to that wall. Positive Wall Offset "
            "moves the run away from the wall."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QtWidgets.QFormLayout()
        self.offset_input = QtWidgets.QDoubleSpinBox()
        self.offset_input.setRange(0.0, 10000.0)
        self.offset_input.setDecimals(1)
        self.offset_input.setValue(0.0)
        self.offset_input.setSuffix(" mm")
        form.addRow("Wall Offset:", self.offset_input)
        layout.addLayout(form)

        self.pick_button = QtWidgets.QPushButton("Pick Wall")
        layout.addWidget(self.pick_button)

        close_button = QtWidgets.QPushButton("Close")
        layout.addWidget(close_button)
        layout.addStretch()

        self.pick_button.clicked.connect(self._pick_wall)
        close_button.clicked.connect(self._close)

    def _pick_wall(self):
        if self.tool is not None:
            self.tool.stop()

        self.tool = CabinetRunSnapWallTool(
            self.run,
            self.offset_input.value(),
        )
        self.tool.start()

    def _close(self):
        if self.tool is not None:
            self.tool.stop()
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        self._close()
        return True

    def reject(self):
        self._close()
        return True
