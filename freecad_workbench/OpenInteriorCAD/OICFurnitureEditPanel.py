"""Task panel for editing OpenInteriorCAD furniture."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets


class FurnitureEditPanel:
    """Task panel for editing a furniture object."""

    def __init__(self, furniture):
        self.furniture = furniture
        self._updating = False

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Edit Furniture"
        )

        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Edit Furniture"
        )

        layout.addWidget(
            title
        )

        self.info_label = QtWidgets.QLabel()

        self.info_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.info_label
        )

        # --------------------------------------------------
        # DIMENSIONS
        # --------------------------------------------------

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
        self.width_input.setDecimals(0)
        self.width_input.setSuffix(" mm")

        dimensions_layout.addRow(
            "Width:",
            self.width_input,
        )

        self.depth_input = QtWidgets.QDoubleSpinBox()
        self.depth_input.setRange(
            50.0,
            10000.0,
        )
        self.depth_input.setDecimals(0)
        self.depth_input.setSuffix(" mm")

        dimensions_layout.addRow(
            "Depth:",
            self.depth_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()
        self.height_input.setRange(
            50.0,
            10000.0,
        )
        self.height_input.setDecimals(0)
        self.height_input.setSuffix(" mm")

        dimensions_layout.addRow(
            "Height:",
            self.height_input,
        )

        layout.addWidget(
            dimensions_group
        )

        # --------------------------------------------------
        # POSITION
        # --------------------------------------------------

        position_group = QtWidgets.QGroupBox(
            "Position"
        )

        position_layout = QtWidgets.QFormLayout(
            position_group
        )

        self.x_input = QtWidgets.QDoubleSpinBox()
        self.x_input.setRange(
            -100000.0,
            100000.0,
        )
        self.x_input.setDecimals(0)
        self.x_input.setSuffix(" mm")

        position_layout.addRow(
            "X:",
            self.x_input,
        )

        self.y_input = QtWidgets.QDoubleSpinBox()
        self.y_input.setRange(
            -100000.0,
            100000.0,
        )
        self.y_input.setDecimals(0)
        self.y_input.setSuffix(" mm")

        position_layout.addRow(
            "Y:",
            self.y_input,
        )

        self.z_input = QtWidgets.QDoubleSpinBox()
        self.z_input.setRange(
            -10000.0,
            10000.0,
        )
        self.z_input.setDecimals(0)
        self.z_input.setSuffix(" mm")

        position_layout.addRow(
            "Z:",
            self.z_input,
        )

        self.rotation_input = QtWidgets.QDoubleSpinBox()
        self.rotation_input.setRange(
            -360.0,
            360.0,
        )
        self.rotation_input.setDecimals(1)
        self.rotation_input.setSuffix("°")

        position_layout.addRow(
            "Rotation:",
            self.rotation_input,
        )

        layout.addWidget(
            position_group
        )

        # --------------------------------------------------
        # QUICK ROTATIONS
        # --------------------------------------------------

        rotation_layout = QtWidgets.QHBoxLayout()

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

        rotation_layout.addWidget(
            self.rotation_0_button
        )

        rotation_layout.addWidget(
            self.rotation_90_button
        )

        rotation_layout.addWidget(
            self.rotation_180_button
        )

        rotation_layout.addWidget(
            self.rotation_270_button
        )

        layout.addLayout(
            rotation_layout
        )

        self.close_button = QtWidgets.QPushButton(
            "Close"
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        # --------------------------------------------------
        # SIGNALS
        # --------------------------------------------------

        self.width_input.valueChanged.connect(
            self._values_changed
        )

        self.depth_input.valueChanged.connect(
            self._values_changed
        )

        self.height_input.valueChanged.connect(
            self._values_changed
        )

        self.x_input.valueChanged.connect(
            self._values_changed
        )

        self.y_input.valueChanged.connect(
            self._values_changed
        )

        self.z_input.valueChanged.connect(
            self._values_changed
        )

        self.rotation_input.valueChanged.connect(
            self._values_changed
        )

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

        self.close_button.clicked.connect(
            self._close
        )

    def _load_values(self):
        """Load current furniture values."""

        self._updating = True

        try:
            self.info_label.setText(
                f"<b>{self.furniture.Label}</b>"
            )

            self.width_input.setValue(
                self.furniture.Width.Value
            )

            self.depth_input.setValue(
                self.furniture.Depth.Value
            )

            self.height_input.setValue(
                self.furniture.Height.Value
            )

            self.x_input.setValue(
                self.furniture.Position.x
            )

            self.y_input.setValue(
                self.furniture.Position.y
            )

            self.z_input.setValue(
                self.furniture.Position.z
            )

            self.rotation_input.setValue(
                self.furniture.RotationAngle.Value
            )

        finally:
            self._updating = False

    def _values_changed(
        self,
        *args,
    ):
        """Apply values immediately."""

        if self._updating:
            return

        self._updating = True

        try:
            self.furniture.Width = (
                self.width_input.value()
            )

            self.furniture.Depth = (
                self.depth_input.value()
            )

            self.furniture.Height = (
                self.height_input.value()
            )

            self.furniture.Position = App.Vector(
                self.x_input.value(),
                self.y_input.value(),
                self.z_input.value(),
            )

            self.furniture.RotationAngle = (
                self.rotation_input.value()
            )

            self.furniture.Document.recompute()

            try:
                Gui.activeDocument().activeView().redraw()

            except Exception:
                pass

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD furniture edit error: "
                f"{error}\n"
            )

        finally:
            self._updating = False

    def _close(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True