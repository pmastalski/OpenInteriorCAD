"""Task panel for adding an OpenInteriorCAD window."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICWindow import create_window


class WindowPanel:
    """Task panel for inserting a window."""

    def __init__(
        self,
        wall,
    ):
        self.wall = wall

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Dodaj okno"
        )

        self._build_ui()
        self._load_wall()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Dodaj okno"
        )

        layout.addWidget(title)

        self.wall_label = QtWidgets.QLabel()
        self.wall_label.setWordWrap(True)

        layout.addWidget(
            self.wall_label
        )

        group = QtWidgets.QGroupBox(
            "Parametry okna"
        )

        form = QtWidgets.QFormLayout(
            group
        )

        self.width_input = QtWidgets.QDoubleSpinBox()
        self.width_input.setRange(
            300.0,
            10000.0,
        )
        self.width_input.setDecimals(0)
        self.width_input.setValue(1200.0)
        self.width_input.setSuffix(" mm")

        form.addRow(
            "Szerokość:",
            self.width_input,
        )

        self.height_input = QtWidgets.QDoubleSpinBox()
        self.height_input.setRange(
            300.0,
            5000.0,
        )
        self.height_input.setDecimals(0)
        self.height_input.setValue(1500.0)
        self.height_input.setSuffix(" mm")

        form.addRow(
            "Wysokość:",
            self.height_input,
        )

        self.sill_input = QtWidgets.QDoubleSpinBox()
        self.sill_input.setRange(
            0.0,
            5000.0,
        )
        self.sill_input.setDecimals(0)
        self.sill_input.setValue(900.0)
        self.sill_input.setSuffix(" mm")

        form.addRow(
            "Wysokość parapetu:",
            self.sill_input,
        )

        self.offset_input = QtWidgets.QDoubleSpinBox()
        self.offset_input.setRange(
            0.0,
            100000.0,
        )
        self.offset_input.setDecimals(0)
        self.offset_input.setValue(800.0)
        self.offset_input.setSuffix(" mm")

        form.addRow(
            "Od początku ściany:",
            self.offset_input,
        )

        layout.addWidget(group)

        self.info_label = QtWidgets.QLabel(
            "Pozycja okna jest liczona od początku "
            "wybranej ściany."
        )
        self.info_label.setWordWrap(True)

        layout.addWidget(
            self.info_label
        )

        self.add_button = QtWidgets.QPushButton(
            "Dodaj okno"
        )

        self.close_button = QtWidgets.QPushButton(
            "Zamknij"
        )

        layout.addWidget(
            self.add_button
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        self.add_button.clicked.connect(
            self._add_window
        )

        self.close_button.clicked.connect(
            self._close
        )

        self.width_input.valueChanged.connect(
            self._update_limits
        )

        self.height_input.valueChanged.connect(
            self._update_limits
        )

        self.sill_input.valueChanged.connect(
            self._update_limits
        )

    def _load_wall(self):
        self.wall_label.setText(
            f"<b>Ściana:</b> {self.wall.Label}<br>"
            f"Długość: {self.wall.Length.Value:.0f} mm<br>"
            f"Wysokość: {self.wall.Height.Value:.0f} mm"
        )

        self._update_limits()

    def _update_limits(self, *args):
        wall_length = (
            self.wall.Length.Value
        )

        wall_height = (
            self.wall.Height.Value
        )

        maximum_offset = max(
            0.0,
            wall_length
            - self.width_input.value(),
        )

        self.offset_input.setMaximum(
            maximum_offset
        )

        maximum_sill = max(
            0.0,
            wall_height
            - self.height_input.value(),
        )

        self.sill_input.setMaximum(
            maximum_sill
        )

        maximum_height = max(
            300.0,
            wall_height
            - self.sill_input.value(),
        )

        self.height_input.setMaximum(
            maximum_height
        )

    def _add_window(self):
        document = self.wall.Document

        if document is None:
            return

        document.openTransaction(
            "Dodaj okno"
        )

        try:
            window = create_window(
                document=document,
                wall=self.wall,
                width=self.width_input.value(),
                height=self.height_input.value(),
                sill_height=self.sill_input.value(),
                offset=self.offset_input.value(),
            )

            room = self._find_room()

            if room is not None:
                room.addObject(
                    window
                )

            document.recompute()
            document.commitTransaction()

        except Exception as error:
            document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD: błąd dodawania okna: "
                f"{error}\n"
            )

            return

        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(
            window
        )

        self.info_label.setText(
            "Okno dodane: "
            f"{window.Width.Value:.0f} × "
            f"{window.Height.Value:.0f} mm, "
            f"parapet {window.SillHeight.Value:.0f} mm."
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