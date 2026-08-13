"""Task panel for inserting furniture."""

import FreeCADGui as Gui
from PySide import QtWidgets


class FurniturePanel:
    """Panel for inserting a cabinet."""

    def __init__(
        self,
        tool,
    ):
        self.tool = tool

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Add Cabinet"
        )

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Add Cabinet"
        )

        layout.addWidget(
            title
        )

        self.status_label = QtWidgets.QLabel(
            "Enter cabinet dimensions."
        )

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        dimensions_group = QtWidgets.QGroupBox(
            "Dimensions"
        )

        dimensions_layout = QtWidgets.QFormLayout(
            dimensions_group
        )

        self.width_input = QtWidgets.QDoubleSpinBox()

        self.width_input.setRange(
            50.0,
            10000.0,
        )

        self.width_input.setDecimals(
            0
        )

        self.width_input.setValue(
            600.0
        )

        self.width_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Width:",
            self.width_input,
        )

        self.depth_input = QtWidgets.QDoubleSpinBox()

        self.depth_input.setRange(
            50.0,
            10000.0,
        )

        self.depth_input.setDecimals(
            0
        )

        self.depth_input.setValue(
            600.0
        )

        self.depth_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Depth:",
            self.depth_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()

        self.height_input.setRange(
            50.0,
            10000.0,
        )

        self.height_input.setDecimals(
            0
        )

        self.height_input.setValue(
            850.0
        )

        self.height_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Height:",
            self.height_input,
        )

        self.rotation_input = QtWidgets.QDoubleSpinBox()

        self.rotation_input.setRange(
            -360.0,
            360.0,
        )

        self.rotation_input.setDecimals(
            1
        )

        self.rotation_input.setValue(
            0.0
        )

        self.rotation_input.setSuffix(
            "°"
        )

        dimensions_layout.addRow(
            "Rotation:",
            self.rotation_input,
        )

        layout.addWidget(
            dimensions_group
        )

        rotation_buttons = QtWidgets.QHBoxLayout()

        self.rotation_0_button = QtWidgets.QPushButton(
            "0°"
        )

        self.rotation_90_button = QtWidgets.QPushButton(
            "90°"
        )

        self.rotation_180_button = QtWidgets.QPushButton(
            "180°"
        )

        self.rotation_270_button = QtWidgets.QPushButton(
            "270°"
        )

        rotation_buttons.addWidget(
            self.rotation_0_button
        )

        rotation_buttons.addWidget(
            self.rotation_90_button
        )

        rotation_buttons.addWidget(
            self.rotation_180_button
        )

        rotation_buttons.addWidget(
            self.rotation_270_button
        )

        layout.addLayout(
            rotation_buttons
        )

        self.place_button = QtWidgets.QPushButton(
            "Pick Position"
        )

        layout.addWidget(
            self.place_button
        )

        self.close_button = QtWidgets.QPushButton(
            "Close"
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        self.rotation_0_button.clicked.connect(
            lambda: self.rotation_input.setValue(
                0.0
            )
        )

        self.rotation_90_button.clicked.connect(
            lambda: self.rotation_input.setValue(
                90.0
            )
        )

        self.rotation_180_button.clicked.connect(
            lambda: self.rotation_input.setValue(
                180.0
            )
        )

        self.rotation_270_button.clicked.connect(
            lambda: self.rotation_input.setValue(
                270.0
            )
        )

        self.place_button.clicked.connect(
            self._start_placement
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _start_placement(self):
        self.tool.start_placement(
            width=self.width_input.value(),
            depth=self.depth_input.value(),
            height=self.height_input.value(),
            rotation=self.rotation_input.value(),
        )

        self.status_label.setText(
            "Click in the view where "
            "the cabinet should be placed."
        )

    def placement_finished(
        self,
        furniture,
    ):
        self.status_label.setText(
            "Cabinet added. "
            "You can pick another position."
        )

    def placement_cancelled(
        self,
    ):
        self.status_label.setText(
            "Placement cancelled."
        )

    def _close(self):
        self.tool.stop(
            close_panel=True
        )

    def getStandardButtons(self):
        return 0

    def accept(self):
        self.tool.stop(
            close_panel=False
        )

        return True

    def reject(self):
        self.tool.stop(
            close_panel=False
        )

        return True