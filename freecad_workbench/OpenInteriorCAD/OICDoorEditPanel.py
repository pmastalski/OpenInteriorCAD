"""Task panel for editing OpenInteriorCAD doors."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICDoor import (
    SWING_LEFT,
    SWING_RIGHT,
    DIRECTION_IN,
    DIRECTION_OUT,
)


class DoorEditPanel:
    """Task panel for editing an existing door."""

    def __init__(self, door):
        self.door = door
        self.wall = door.HostWall

        self._updating = False

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Edytuj drzwi")

        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Edytuj drzwi"
        )
        layout.addWidget(title)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # ------------------------------------------
        # WYMIARY
        # ------------------------------------------

        dimensions_group = QtWidgets.QGroupBox(
            "Wymiary i położenie"
        )

        dimensions_layout = QtWidgets.QFormLayout(
            dimensions_group
        )

        self.width_input = QtWidgets.QDoubleSpinBox()
        self.width_input.setRange(
            300.0,
            5000.0,
        )
        self.width_input.setDecimals(0)
        self.width_input.setSuffix(" mm")

        dimensions_layout.addRow(
            "Szerokość:",
            self.width_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()
        self.height_input.setRange(
            500.0,
            5000.0,
        )
        self.height_input.setDecimals(0)
        self.height_input.setSuffix(" mm")

        dimensions_layout.addRow(
            "Wysokość:",
            self.height_input,
        )

        self.offset_input = QtWidgets.QDoubleSpinBox()
        self.offset_input.setRange(
            0.0,
            100000.0,
        )
        self.offset_input.setDecimals(0)
        self.offset_input.setSuffix(" mm")

        dimensions_layout.addRow(
            "Od początku ściany:",
            self.offset_input,
        )

        layout.addWidget(
            dimensions_group
        )

        # ------------------------------------------
        # OTWIERANIE
        # ------------------------------------------

        swing_group = QtWidgets.QGroupBox(
            "Otwieranie"
        )

        swing_layout = QtWidgets.QFormLayout(
            swing_group
        )

        self.side_combo = QtWidgets.QComboBox()

        self.side_combo.addItems(
            [
                SWING_LEFT,
                SWING_RIGHT,
            ]
        )

        swing_layout.addRow(
            "Zawiasy:",
            self.side_combo,
        )

        self.direction_combo = QtWidgets.QComboBox()

        self.direction_combo.addItems(
            [
                DIRECTION_IN,
                DIRECTION_OUT,
            ]
        )

        swing_layout.addRow(
            "Kierunek:",
            self.direction_combo,
        )

        layout.addWidget(
            swing_group
        )

        # ------------------------------------------
        # PRZYCISKI
        # ------------------------------------------

        self.close_button = QtWidgets.QPushButton(
            "Zamknij"
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        # ------------------------------------------
        # SIGNALS
        # ------------------------------------------

        self.width_input.valueChanged.connect(
            self._values_changed
        )

        self.height_input.valueChanged.connect(
            self._values_changed
        )

        self.offset_input.valueChanged.connect(
            self._values_changed
        )

        self.side_combo.currentTextChanged.connect(
            self._values_changed
        )

        self.direction_combo.currentTextChanged.connect(
            self._values_changed
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _load_values(self):
        """Load current door values into the panel."""

        self._updating = True

        try:
            wall_length = (
                self.wall.Length.Value
            )

            self.width_input.setMaximum(
                max(
                    300.0,
                    wall_length - 1.0,
                )
            )

            self.width_input.setValue(
                self.door.Width.Value
            )

            self.height_input.setMaximum(
                self.wall.Height.Value
            )

            self.height_input.setValue(
                self.door.Height.Value
            )

            maximum_offset = max(
                0.0,
                wall_length
                - self.door.Width.Value,
            )

            self.offset_input.setMaximum(
                maximum_offset
            )

            self.offset_input.setValue(
                self.door.Offset.Value
            )

            side_index = (
                self.side_combo.findText(
                    str(
                        self.door.SwingSide
                    )
                )
            )

            if side_index >= 0:
                self.side_combo.setCurrentIndex(
                    side_index
                )

            direction_index = (
                self.direction_combo.findText(
                    str(
                        self.door.SwingDirection
                    )
                )
            )

            if direction_index >= 0:
                self.direction_combo.setCurrentIndex(
                    direction_index
                )

            self.info_label.setText(
                f"<b>{self.door.Label}</b><br>"
                f"Ściana: {self.wall.Label}<br>"
                f"Długość ściany: "
                f"{wall_length:.0f} mm"
            )

        finally:
            self._updating = False

    def _values_changed(self, *args):
        """Apply changes immediately."""

        if self._updating:
            return

        if self.door is None:
            return

        if self.wall is None:
            return

        self._updating = True

        try:
            width = (
                self.width_input.value()
            )

            maximum_offset = max(
                0.0,
                self.wall.Length.Value
                - width,
            )

            self.offset_input.setMaximum(
                maximum_offset
            )

            if (
                self.offset_input.value()
                > maximum_offset
            ):
                self.offset_input.setValue(
                    maximum_offset
                )

            self.door.Width = width

            self.door.Height = (
                self.height_input.value()
            )

            self.door.Offset = (
                self.offset_input.value()
            )

            self.door.SwingSide = (
                self.side_combo.currentText()
            )

            self.door.SwingDirection = (
                self.direction_combo.currentText()
            )

            self.door.Document.recompute()

            try:
                Gui.activeDocument().activeView().redraw()
            except Exception:
                pass

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD: błąd edycji drzwi: "
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