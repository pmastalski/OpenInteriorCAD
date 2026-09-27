"""Task panel for standalone OpenInteriorCAD filler elements."""

from __future__ import annotations

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from OICBoardElement import OIC_TYPE


class BoardElementEditPanel:
    def __init__(self, element):
        self.element = element
        self._updating = False
        self._selection_observer_installed = False

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            f"Edit Filler - {element.Label}"
        )

        layout = QtWidgets.QVBoxLayout(self.form)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        dimensions = QtWidgets.QGroupBox("Dimensions")
        dimensions_layout = QtWidgets.QFormLayout(dimensions)

        self.width_input = self._length_spin(1.0, 5000.0)
        self.height_input = self._length_spin(1.0, 5000.0)
        self.thickness_input = self._length_spin(0.1, 200.0)

        dimensions_layout.addRow("Width:", self.width_input)
        dimensions_layout.addRow("Height:", self.height_input)
        dimensions_layout.addRow("Thickness:", self.thickness_input)

        layout.addWidget(dimensions)

        placement = QtWidgets.QGroupBox("Placement")
        placement_layout = QtWidgets.QFormLayout(placement)

        self.x_input = self._length_spin(-100000.0, 100000.0)
        self.y_input = self._length_spin(-100000.0, 100000.0)
        self.z_input = self._length_spin(-100000.0, 100000.0)
        self.rotation_input = QtWidgets.QDoubleSpinBox()
        self.rotation_input.setRange(-360.0, 360.0)
        self.rotation_input.setDecimals(2)
        self.rotation_input.setSuffix(" °")

        placement_layout.addRow("X:", self.x_input)
        placement_layout.addRow("Y:", self.y_input)
        placement_layout.addRow("Z:", self.z_input)
        placement_layout.addRow("Rotation Z:", self.rotation_input)

        layout.addWidget(placement)

        edges = QtWidgets.QGroupBox("Edge Banding")
        edges_layout = QtWidgets.QGridLayout(edges)

        self.edge_top_check = QtWidgets.QCheckBox("Top")
        self.edge_bottom_check = QtWidgets.QCheckBox("Bottom")
        self.edge_left_check = QtWidgets.QCheckBox("Left")
        self.edge_right_check = QtWidgets.QCheckBox("Right")

        edges_layout.addWidget(self.edge_top_check, 0, 0)
        edges_layout.addWidget(self.edge_bottom_check, 0, 1)
        edges_layout.addWidget(self.edge_left_check, 1, 0)
        edges_layout.addWidget(self.edge_right_check, 1, 1)

        layout.addWidget(edges)

        production = QtWidgets.QGroupBox("Production")
        production_layout = QtWidgets.QFormLayout(production)

        self.board_material_input = QtWidgets.QLineEdit()
        self.edge_material_input = QtWidgets.QLineEdit()
        self.edge_thickness_input = self._length_spin(0.0, 20.0)

        production_layout.addRow("Board Material:", self.board_material_input)
        production_layout.addRow("Edge Material:", self.edge_material_input)
        production_layout.addRow("Edge Thickness:", self.edge_thickness_input)

        layout.addWidget(production)

        nav_help = QtWidgets.QLabel(
            "Changes apply immediately. While this editor is open you can "
            "click another OpenInteriorCAD filler in the 3D view or Model tree."
        )
        nav_help.setWordWrap(True)
        layout.addWidget(nav_help)

        close_button = QtWidgets.QPushButton("Close Editor")
        close_button.clicked.connect(self._close_editor)
        layout.addWidget(close_button)
        layout.addStretch(1)

        for widget in (
            self.width_input,
            self.height_input,
            self.thickness_input,
            self.x_input,
            self.y_input,
            self.z_input,
            self.rotation_input,
            self.edge_thickness_input,
        ):
            widget.valueChanged.connect(self._values_changed)

        for widget in (
            self.edge_top_check,
            self.edge_bottom_check,
            self.edge_left_check,
            self.edge_right_check,
        ):
            widget.toggled.connect(self._values_changed)

        self.board_material_input.textChanged.connect(self._values_changed)
        self.edge_material_input.textChanged.connect(self._values_changed)

        self._load_values()
        self._install_selection_observer()

    @staticmethod
    def _length_spin(minimum, maximum):
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(2)
        spin.setSuffix(" mm")
        return spin

    def _load_values(self):
        self._updating = True
        try:
            obj = self.element
            self.info_label.setText(
                f"<b>{obj.Label}</b><br>Standalone filler / board element."
            )

            self.width_input.setValue(float(obj.Width.Value))
            self.height_input.setValue(float(obj.Height.Value))
            self.thickness_input.setValue(float(obj.Thickness.Value))

            base = obj.Placement.Base
            self.x_input.setValue(float(base.x))
            self.y_input.setValue(float(base.y))
            self.z_input.setValue(float(base.z))

            try:
                angle = float(obj.Placement.Rotation.Angle) * 180.0 / 3.141592653589793
                axis = obj.Placement.Rotation.Axis
                if axis.z < 0:
                    angle *= -1.0
            except Exception:
                angle = 0.0
            self.rotation_input.setValue(angle)

            self.edge_top_check.setChecked(bool(obj.EdgeTop))
            self.edge_bottom_check.setChecked(bool(obj.EdgeBottom))
            self.edge_left_check.setChecked(bool(obj.EdgeLeft))
            self.edge_right_check.setChecked(bool(obj.EdgeRight))

            self.board_material_input.setText(str(obj.BoardMaterial))
            self.edge_material_input.setText(str(obj.EdgeMaterial))
            self.edge_thickness_input.setValue(float(obj.EdgeThickness.Value))

            self.form.setWindowTitle(f"Edit Filler - {obj.Label}")
        finally:
            self._updating = False

    def _values_changed(self, *args):
        if self._updating:
            return

        obj = self.element
        try:
            obj.Width = self.width_input.value()
            obj.Height = self.height_input.value()
            obj.Thickness = self.thickness_input.value()

            obj.Placement = App.Placement(
                App.Vector(
                    self.x_input.value(),
                    self.y_input.value(),
                    self.z_input.value(),
                ),
                App.Rotation(
                    App.Vector(0.0, 0.0, 1.0),
                    self.rotation_input.value(),
                ),
            )

            obj.EdgeTop = self.edge_top_check.isChecked()
            obj.EdgeBottom = self.edge_bottom_check.isChecked()
            obj.EdgeLeft = self.edge_left_check.isChecked()
            obj.EdgeRight = self.edge_right_check.isChecked()

            obj.BoardMaterial = self.board_material_input.text().strip()
            obj.EdgeMaterial = self.edge_material_input.text().strip()
            obj.EdgeThickness = self.edge_thickness_input.value()

            obj.Document.recompute()
        except Exception as error:
            App.Console.PrintError(
                f"OpenInteriorCAD filler edit error: {error}\n"
            )

    def _install_selection_observer(self):
        if self._selection_observer_installed:
            return
        Gui.Selection.addObserver(self)
        self._selection_observer_installed = True

    def _remove_selection_observer(self):
        if not self._selection_observer_installed:
            return
        try:
            Gui.Selection.removeObserver(self)
        except Exception:
            pass
        self._selection_observer_installed = False

    def addSelection(self, document_name, object_name, sub_name="", point=None):
        if self._updating:
            return

        try:
            doc = App.getDocument(document_name)
            obj = doc.getObject(object_name)
        except Exception:
            return

        if (
            obj is None
            or getattr(obj, "OICType", "") != OIC_TYPE
            or obj is self.element
        ):
            return

        self.element = obj
        self._load_values()

    def removeSelection(self, *args):
        return

    def clearSelection(self, *args):
        return

    def setSelection(self, *args):
        return

    def _close_editor(self):
        self._remove_selection_observer()
        Gui.Control.closeDialog()

    def accept(self):
        self._remove_selection_observer()
        return True

    def reject(self):
        self._remove_selection_observer()
        return True

    def getStandardButtons(self):
        return 0
