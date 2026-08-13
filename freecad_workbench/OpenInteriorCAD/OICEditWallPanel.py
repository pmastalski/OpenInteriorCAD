"""Task panel for editing an OpenInteriorCAD wall."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICDimensions import (
    update_room_dimensions,
)
from OICWall import (
    REFERENCE_AXIS,
    REFERENCE_LEFT,
    REFERENCE_RIGHT,
    rebuild_from_wall,
)


class EditWallPanel:
    """Task Panel for editing one selected wall."""

    def __init__(
        self,
        wall,
    ):
        self.wall = wall

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Edytuj ścianę"
        )

        self._build_ui()
        self._load_wall()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Edycja ściany"
        )

        main_layout.addWidget(
            title
        )

        self.wall_name_label = QtWidgets.QLabel()

        self.wall_name_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.wall_name_label
        )

        geometry_group = QtWidgets.QGroupBox(
            "Geometria"
        )

        geometry_layout = QtWidgets.QFormLayout(
            geometry_group
        )

        self.length_input = QtWidgets.QDoubleSpinBox()

        self.length_input.setRange(
            1.0,
            100000.0,
        )

        self.length_input.setDecimals(
            0
        )

        self.length_input.setSuffix(
            " mm"
        )

        geometry_layout.addRow(
            "Długość:",
            self.length_input,
        )

        self.angle_input = QtWidgets.QDoubleSpinBox()

        self.angle_input.setRange(
            -360.0,
            360.0,
        )

        self.angle_input.setDecimals(
            1
        )

        self.angle_input.setSuffix(
            "°"
        )

        geometry_layout.addRow(
            "Kąt:",
            self.angle_input,
        )

        self.angle_info = QtWidgets.QLabel()

        self.angle_info.setWordWrap(
            True
        )

        geometry_layout.addRow(
            self.angle_info
        )

        self.thickness_input = QtWidgets.QDoubleSpinBox()

        self.thickness_input.setRange(
            1.0,
            5000.0,
        )

        self.thickness_input.setDecimals(
            0
        )

        self.thickness_input.setSuffix(
            " mm"
        )

        geometry_layout.addRow(
            "Grubość:",
            self.thickness_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()

        self.height_input.setRange(
            1.0,
            20000.0,
        )

        self.height_input.setDecimals(
            0
        )

        self.height_input.setSuffix(
            " mm"
        )

        geometry_layout.addRow(
            "Wysokość:",
            self.height_input,
        )

        self.reference_combo = QtWidgets.QComboBox()

        self.reference_combo.addItems(
            [
                REFERENCE_AXIS,
                REFERENCE_LEFT,
                REFERENCE_RIGHT,
            ]
        )

        geometry_layout.addRow(
            "Linia odniesienia:",
            self.reference_combo,
        )

        main_layout.addWidget(
            geometry_group
        )

        calculated_group = QtWidgets.QGroupBox(
            "Wartości obliczone"
        )

        calculated_layout = QtWidgets.QFormLayout(
            calculated_group
        )

        self.heading_label = QtWidgets.QLabel()

        calculated_layout.addRow(
            "Kierunek bezwzględny:",
            self.heading_label,
        )

        self.start_label = QtWidgets.QLabel()

        calculated_layout.addRow(
            "Początek:",
            self.start_label,
        )

        self.end_label = QtWidgets.QLabel()

        calculated_layout.addRow(
            "Koniec:",
            self.end_label,
        )

        main_layout.addWidget(
            calculated_group
        )

        self.apply_button = QtWidgets.QPushButton(
            "Zastosuj"
        )

        main_layout.addWidget(
            self.apply_button
        )

        self.close_button = QtWidgets.QPushButton(
            "Zamknij"
        )

        main_layout.addWidget(
            self.close_button
        )

        main_layout.addStretch()

        self.apply_button.clicked.connect(
            self._apply
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _load_wall(self):
        self.wall_name_label.setText(
            f"<b>{self.wall.Label}</b>"
        )

        self.length_input.setValue(
            self.wall.Length.Value
        )

        self.angle_input.setValue(
            self.wall.Angle.Value
        )

        self.thickness_input.setValue(
            self.wall.Thickness.Value
        )

        self.height_input.setValue(
            self.wall.Height.Value
        )

        index = self.reference_combo.findText(
            str(
                self.wall.ReferenceLine
            )
        )

        if index >= 0:
            self.reference_combo.setCurrentIndex(
                index
            )

        room = self._find_room()

        if room is not None:
            walls = self._get_room_walls(
                room
            )

            if (
                walls
                and walls[0] == self.wall
            ):
                self.angle_info.setText(
                    "Pierwsza ściana: "
                    "kąt względem osi X."
                )

            else:
                self.angle_info.setText(
                    "Kąt względem poprzedniej ściany."
                )

        if getattr(
            self.wall,
            "AutoClose",
            False,
        ):
            self.angle_info.setText(
                "Automatyczna ściana zamykająca. "
                "Długość i kąt są wyliczane."
            )

            self.length_input.setEnabled(
                False
            )

            self.angle_input.setEnabled(
                False
            )

        self._update_calculated_labels()

    def _apply(self):
        document = self.wall.Document

        if document is None:
            return

        document.openTransaction(
            "Edytuj ścianę"
        )

        try:
            if not getattr(
                self.wall,
                "AutoClose",
                False,
            ):
                self.wall.Length = (
                    self.length_input.value()
                )

                self.wall.Angle = (
                    self.angle_input.value()
                )

            self.wall.Thickness = (
                self.thickness_input.value()
            )

            self.wall.Height = (
                self.height_input.value()
            )

            self.wall.ReferenceLine = (
                self.reference_combo.currentText()
            )

            rebuild_from_wall(
                self.wall
            )

            room = self._find_room()

            if (
                room is not None
                and getattr(
                    room,
                    "ShowDimensions",
                    True,
                )
            ):
                update_room_dimensions(
                    room
                )

            document.recompute()

            document.commitTransaction()

        except Exception as error:
            document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD: błąd edycji ściany: "
                f"{error}\n"
            )

            return

        self._update_calculated_labels()

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            self.wall
        )

        try:
            Gui.activeDocument().activeView().fitAll()

        except Exception:
            pass

    def _update_calculated_labels(self):
        self.heading_label.setText(
            f"{self.wall.Heading.Value:.1f}°"
        )

        self.start_label.setText(
            self._format_point(
                self.wall.StartPoint
            )
        )

        self.end_label.setText(
            self._format_point(
                self.wall.EndPoint
            )
        )

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

    @staticmethod
    def _get_room_walls(
        room,
    ):
        return [
            obj
            for obj in room.Group
            if getattr(
                obj,
                "OICType",
                "",
            )
            == "OpenInteriorCAD::Wall"
        ]

    @staticmethod
    def _format_point(
        point,
    ):
        return (
            f"X: {point.x:.0f} mm, "
            f"Y: {point.y:.0f} mm"
        )

    def _close(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True