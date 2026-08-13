"""Task panel for editing OpenInteriorCAD windows."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets


class WindowEditPanel:
    """Task panel for editing an existing window."""

    def __init__(
        self,
        window,
    ):
        self.window = window
        self.wall = window.HostWall

        self._updating = False

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Edit Window"
        )

        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Edit Window"
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

        group = QtWidgets.QGroupBox(
            "Dimensions and Position"
        )

        form = QtWidgets.QFormLayout(
            group
        )

        self.width_input = QtWidgets.QDoubleSpinBox()

        self.width_input.setRange(
            300.0,
            10000.0,
        )

        self.width_input.setDecimals(
            0
        )

        self.width_input.setSuffix(
            " mm"
        )

        form.addRow(
            "Width:",
            self.width_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()

        self.height_input.setRange(
            300.0,
            5000.0,
        )

        self.height_input.setDecimals(
            0
        )

        self.height_input.setSuffix(
            " mm"
        )

        form.addRow(
            "Height:",
            self.height_input,
        )

        self.sill_input = QtWidgets.QDoubleSpinBox()

        self.sill_input.setRange(
            0.0,
            5000.0,
        )

        self.sill_input.setDecimals(
            0
        )

        self.sill_input.setSuffix(
            " mm"
        )

        form.addRow(
            "Sill Height:",
            self.sill_input,
        )

        self.offset_input = QtWidgets.QDoubleSpinBox()

        self.offset_input.setRange(
            0.0,
            100000.0,
        )

        self.offset_input.setDecimals(
            0
        )

        self.offset_input.setSuffix(
            " mm"
        )

        form.addRow(
            "From Wall Start:",
            self.offset_input,
        )

        layout.addWidget(
            group
        )

        self.close_button = QtWidgets.QPushButton(
            "Close"
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        self.width_input.valueChanged.connect(
            self._values_changed
        )

        self.height_input.valueChanged.connect(
            self._values_changed
        )

        self.sill_input.valueChanged.connect(
            self._values_changed
        )

        self.offset_input.valueChanged.connect(
            self._values_changed
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _load_values(self):
        """Load current window parameters."""

        self._updating = True

        try:
            self.info_label.setText(
                f"<b>{self.window.Label}</b><br>"
                f"Wall: {self.wall.Label}<br>"
                f"Wall length: "
                f"{self.wall.Length.Value:.0f} mm<br>"
                f"Wall height: "
                f"{self.wall.Height.Value:.0f} mm"
            )

            self.width_input.setMaximum(
                max(
                    300.0,
                    self.wall.Length.Value - 1.0,
                )
            )

            self.width_input.setValue(
                self.window.Width.Value
            )

            self.height_input.setMaximum(
                self.wall.Height.Value
            )

            self.height_input.setValue(
                self.window.Height.Value
            )

            self.sill_input.setMaximum(
                max(
                    0.0,
                    self.wall.Height.Value
                    - self.window.Height.Value,
                )
            )

            self.sill_input.setValue(
                self.window.SillHeight.Value
            )

            self.offset_input.setMaximum(
                max(
                    0.0,
                    self.wall.Length.Value
                    - self.window.Width.Value,
                )
            )

            self.offset_input.setValue(
                self.window.Offset.Value
            )

        finally:
            self._updating = False

    def _values_changed(
        self,
        *args,
    ):
        """Apply changes live."""

        if self._updating:
            return

        if self.window is None:
            return

        if self.wall is None:
            return

        self._updating = True

        try:
            width = (
                self.width_input.value()
            )

            height = (
                self.height_input.value()
            )

            sill = (
                self.sill_input.value()
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

            maximum_sill = max(
                0.0,
                self.wall.Height.Value
                - height,
            )

            self.sill_input.setMaximum(
                maximum_sill
            )

            if sill > maximum_sill:
                sill = maximum_sill

                self.sill_input.setValue(
                    sill
                )

            maximum_height = max(
                300.0,
                self.wall.Height.Value
                - sill,
            )

            self.height_input.setMaximum(
                maximum_height
            )

            if height > maximum_height:
                height = maximum_height

                self.height_input.setValue(
                    height
                )

            self.window.Width = width

            self.window.Height = height

            self.window.SillHeight = sill

            self.window.Offset = (
                self.offset_input.value()
            )

            self.window.Document.recompute()

            try:
                Gui.activeDocument().activeView().redraw()

            except Exception:
                pass

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD window edit error: "
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