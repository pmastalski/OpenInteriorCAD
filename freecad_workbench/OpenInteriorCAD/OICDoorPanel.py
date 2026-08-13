"""Task panel for adding an OpenInteriorCAD door."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICDoor import create_door


class DoorPanel:
    """Task Panel for inserting a door into a wall."""

    def __init__(
        self,
        wall,
    ):
        self.wall = wall
        self.door = None

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Add Door"
        )

        self._build_ui()
        self._load_wall()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Add Door"
        )

        main_layout.addWidget(
            title
        )

        self.wall_label = QtWidgets.QLabel()

        self.wall_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.wall_label
        )

        parameters_group = QtWidgets.QGroupBox(
            "Door Parameters"
        )

        parameters_layout = QtWidgets.QFormLayout(
            parameters_group
        )

        self.width_input = QtWidgets.QDoubleSpinBox()

        self.width_input.setRange(
            300.0,
            5000.0,
        )

        self.width_input.setDecimals(
            0
        )

        self.width_input.setValue(
            900.0
        )

        self.width_input.setSuffix(
            " mm"
        )

        parameters_layout.addRow(
            "Width:",
            self.width_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()

        self.height_input.setRange(
            500.0,
            5000.0,
        )

        self.height_input.setDecimals(
            0
        )

        self.height_input.setValue(
            2100.0
        )

        self.height_input.setSuffix(
            " mm"
        )

        parameters_layout.addRow(
            "Height:",
            self.height_input,
        )

        self.offset_input = QtWidgets.QDoubleSpinBox()

        self.offset_input.setRange(
            0.0,
            100000.0,
        )

        self.offset_input.setDecimals(
            0
        )

        self.offset_input.setValue(
            500.0
        )

        self.offset_input.setSuffix(
            " mm"
        )

        parameters_layout.addRow(
            "From Wall Start:",
            self.offset_input,
        )

        main_layout.addWidget(
            parameters_group
        )

        self.info_label = QtWidgets.QLabel(
            "Distance is measured from the start "
            "of the selected wall axis."
        )

        self.info_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.info_label
        )

        self.add_button = QtWidgets.QPushButton(
            "Add Door"
        )

        main_layout.addWidget(
            self.add_button
        )

        self.close_button = QtWidgets.QPushButton(
            "Close"
        )

        main_layout.addWidget(
            self.close_button
        )

        main_layout.addStretch()

        self.add_button.clicked.connect(
            self._add_door
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _load_wall(self):
        self.wall_label.setText(
            (
                f"<b>Wall:</b> {self.wall.Label}<br>"
                f"Length: {self.wall.Length.Value:.0f} mm"
            )
        )

        maximum_offset = max(
            0.0,
            self.wall.Length.Value
            - self.width_input.value(),
        )

        self.offset_input.setMaximum(
            maximum_offset
        )

        self.width_input.valueChanged.connect(
            self._update_offset_range
        )

    def _update_offset_range(self):
        maximum_offset = max(
            0.0,
            self.wall.Length.Value
            - self.width_input.value(),
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

    def _add_door(self):
        document = self.wall.Document

        if document is None:
            return

        width = self.width_input.value()
        height = self.height_input.value()
        offset = self.offset_input.value()

        if width >= self.wall.Length.Value:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Add Door",
                (
                    "Door width must be smaller "
                    "than the wall length."
                ),
            )
            return

        document.openTransaction(
            "Add Door"
        )

        try:
            self.door = create_door(
                document=document,
                wall=self.wall,
                width=width,
                height=height,
                offset=offset,
            )

            room = self._find_room()

            if room is not None:
                room.addObject(
                    self.door
                )

            document.recompute()

            document.commitTransaction()

        except Exception as error:
            document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD door add error: "
                f"{error}\n"
            )
            return

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            self.door
        )

        self.info_label.setText(
            (
                "Door added: "
                f"{width:.0f} × {height:.0f} mm, "
                f"offset {offset:.0f} mm."
            )
        )

        try:
            Gui.activeDocument().activeView().fitAll()
        except Exception:
            pass

    def _find_room(self):
        document = self.wall.Document

        if document is None:
            return None

        for obj in document.Objects:
            if (
                getattr(
                    obj,
                    "OICType",
                    "",
                )
                != "OpenInteriorCAD::Room"
            ):
                continue

            if self.wall in obj.Group:
                return obj

        return None

    def _close(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True