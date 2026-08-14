"""Edit panel for the universal OpenInteriorCAD Cabinet."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICFurniture import (
    CABINET_BASE,
    CABINET_WALL,
    CABINET_TALL,
    CABINET_CORNER_BASE,
    CABINET_CORNER_WALL,
    GEOMETRY_BOX,
    GEOMETRY_CARCASS,
    FRONT_OPEN,
    FRONT_SINGLE,
    FRONT_DOUBLE,
    FRONT_DRAWERS,
    FRONT_DOOR_DRAWERS,
    FRONT_LIFT_UP,
    FRONT_CORNER_FOLDING,
)


class FurnitureEditPanel:
    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture
        self._updating = False

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Edit Furniture"
        )

        self._build_ui()
        self._load_values()
        self._update_type_ui()
        self._update_front_ui()

    def _length_spin(
        self,
        minimum=0.0,
        maximum=10000.0,
        decimals=1,
    ):
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(
            minimum,
            maximum,
        )
        spin.setDecimals(
            decimals
        )
        spin.setSuffix(
            " mm"
        )
        return spin

    def _build_ui(
        self,
    ):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        layout.addWidget(
            QtWidgets.QLabel(
                "<b>OpenInteriorCAD</b><br>"
                "Edit Furniture"
            )
        )

        self.info_label = (
            QtWidgets.QLabel()
        )

        layout.addWidget(
            self.info_label
        )

        # GENERAL
        general_group = (
            QtWidgets.QGroupBox(
                "General"
            )
        )

        general_layout = (
            QtWidgets.QFormLayout(
                general_group
            )
        )

        self.type_combo = (
            QtWidgets.QComboBox()
        )

        self.type_combo.addItems(
            [
                CABINET_BASE,
                CABINET_WALL,
                CABINET_TALL,
                CABINET_CORNER_BASE,
                CABINET_CORNER_WALL,
            ]
        )

        self.geometry_combo = (
            QtWidgets.QComboBox()
        )

        self.geometry_combo.addItems(
            [
                GEOMETRY_BOX,
                GEOMETRY_CARCASS,
            ]
        )

        general_layout.addRow(
            "Cabinet Type:",
            self.type_combo,
        )

        general_layout.addRow(
            "Geometry:",
            self.geometry_combo,
        )

        layout.addWidget(
            general_group
        )

        # DIMENSIONS
        dimensions_group = (
            QtWidgets.QGroupBox(
                "Dimensions"
            )
        )

        dimensions_layout = (
            QtWidgets.QFormLayout(
                dimensions_group
            )
        )

        self.width_label = (
            QtWidgets.QLabel(
                "Width:"
            )
        )

        self.depth_label = (
            QtWidgets.QLabel(
                "Depth:"
            )
        )

        self.width_input = (
            self._length_spin(
                50.0,
                10000.0,
            )
        )

        self.depth_input = (
            self._length_spin(
                50.0,
                10000.0,
            )
        )

        self.height_input = (
            self._length_spin(
                50.0,
                10000.0,
            )
        )

        dimensions_layout.addRow(
            self.width_label,
            self.width_input,
        )

        dimensions_layout.addRow(
            self.depth_label,
            self.depth_input,
        )

        dimensions_layout.addRow(
            "Height:",
            self.height_input,
        )

        layout.addWidget(
            dimensions_group
        )

        # CORNER
        self.corner_group = (
            QtWidgets.QGroupBox(
                "Corner Geometry"
            )
        )

        corner_layout = (
            QtWidgets.QFormLayout(
                self.corner_group
            )
        )

        self.width_b_input = (
            self._length_spin(
                50.0,
                10000.0,
            )
        )

        self.depth_b_input = (
            self._length_spin(
                50.0,
                10000.0,
            )
        )

        corner_layout.addRow(
            "Width B:",
            self.width_b_input,
        )

        corner_layout.addRow(
            "Depth B:",
            self.depth_b_input,
        )

        self.corner_opening_input = (
            self._length_spin(
                50.0,
                1500.0,
            )
        )

        corner_layout.addRow(
            "Corner Opening:",
            self.corner_opening_input,
        )

        corner_help = QtWidgets.QLabel(
            "Corner footprint: "
            "A = horizontal leg, "
            "B = perpendicular leg."
        )

        corner_help.setWordWrap(
            True
        )

        corner_layout.addRow(
            corner_help
        )

        layout.addWidget(
            self.corner_group
        )

        # CARCASS
        carcass_group = (
            QtWidgets.QGroupBox(
                "Carcass"
            )
        )

        carcass_layout = (
            QtWidgets.QFormLayout(
                carcass_group
            )
        )

        self.panel_input = (
            self._length_spin(
                1.0,
                100.0,
            )
        )

        self.back_input = (
            self._length_spin(
                1.0,
                100.0,
            )
        )

        self.shelf_input = (
            QtWidgets.QSpinBox()
        )

        self.shelf_input.setRange(
            0,
            30,
        )

        self.plinth_height_input = (
            self._length_spin(
                0.0,
                1000.0,
            )
        )

        self.plinth_setback_input = (
            self._length_spin(
                0.0,
                1000.0,
            )
        )

        carcass_layout.addRow(
            "Panel Thickness:",
            self.panel_input,
        )

        carcass_layout.addRow(
            "Back Thickness:",
            self.back_input,
        )

        carcass_layout.addRow(
            "Shelves:",
            self.shelf_input,
        )

        carcass_layout.addRow(
            "Plinth Height:",
            self.plinth_height_input,
        )

        carcass_layout.addRow(
            "Plinth Setback:",
            self.plinth_setback_input,
        )

        layout.addWidget(
            carcass_group
        )

        # FRONT LAYOUT
        self.front_group = (
            QtWidgets.QGroupBox(
                "Front Layout"
            )
        )

        front_layout = (
            QtWidgets.QFormLayout(
                self.front_group
            )
        )

        self.front_type_combo = (
            QtWidgets.QComboBox()
        )

        self.front_type_combo.addItems(
            [
                FRONT_OPEN,
                FRONT_SINGLE,
                FRONT_DOUBLE,
                FRONT_DRAWERS,
                FRONT_DOOR_DRAWERS,
                FRONT_LIFT_UP,
                FRONT_CORNER_FOLDING,
            ]
        )

        self.front_thickness_input = (
            self._length_spin(
                1.0,
                100.0,
            )
        )

        self.front_gap_input = (
            self._length_spin(
                0.0,
                50.0,
            )
        )

        self.drawer_count_input = (
            QtWidgets.QSpinBox()
        )

        self.drawer_count_input.setRange(
            1,
            12,
        )

        self.drawer_zone_height_input = (
            self._length_spin(
                20.0,
                1000.0,
            )
        )

        front_layout.addRow(
            "Front Type:",
            self.front_type_combo,
        )

        front_layout.addRow(
            "Front Thickness:",
            self.front_thickness_input,
        )

        front_layout.addRow(
            "Front Gap:",
            self.front_gap_input,
        )

        self.drawer_count_label = (
            QtWidgets.QLabel(
                "Drawers:"
            )
        )

        front_layout.addRow(
            self.drawer_count_label,
            self.drawer_count_input,
        )

        self.drawer_zone_label = (
            QtWidgets.QLabel(
                "Drawer Zone Height:"
            )
        )

        front_layout.addRow(
            self.drawer_zone_label,
            self.drawer_zone_height_input,
        )

        layout.addWidget(
            self.front_group
        )

        # WALL CABINET
        self.wall_group = (
            QtWidgets.QGroupBox(
                "Wall Cabinet"
            )
        )

        wall_layout = (
            QtWidgets.QFormLayout(
                self.wall_group
            )
        )

        self.mount_height_input = (
            self._length_spin(
                0.0,
                10000.0,
            )
        )

        self.apply_mount_button = (
            QtWidgets.QPushButton(
                "Apply Mount Height"
            )
        )

        wall_layout.addRow(
            "Mount Height:",
            self.mount_height_input,
        )

        wall_layout.addRow(
            self.apply_mount_button
        )

        layout.addWidget(
            self.wall_group
        )

        # POSITION
        position_group = (
            QtWidgets.QGroupBox(
                "Position"
            )
        )

        position_layout = (
            QtWidgets.QFormLayout(
                position_group
            )
        )

        self.x_input = (
            self._length_spin(
                -100000.0,
                100000.0,
            )
        )

        self.y_input = (
            self._length_spin(
                -100000.0,
                100000.0,
            )
        )

        self.z_input = (
            self._length_spin(
                -10000.0,
                10000.0,
            )
        )

        self.rotation_input = (
            QtWidgets.QDoubleSpinBox()
        )

        self.rotation_input.setRange(
            -360.0,
            360.0,
        )

        self.rotation_input.setDecimals(
            1
        )

        self.rotation_input.setSuffix(
            "°"
        )

        position_layout.addRow(
            "X:",
            self.x_input,
        )

        position_layout.addRow(
            "Y:",
            self.y_input,
        )

        position_layout.addRow(
            "Z:",
            self.z_input,
        )

        position_layout.addRow(
            "Rotation:",
            self.rotation_input,
        )

        layout.addWidget(
            position_group
        )

        close_button = (
            QtWidgets.QPushButton(
                "Close"
            )
        )

        layout.addWidget(
            close_button
        )

        layout.addStretch()

        # SIGNALS
        self.type_combo.currentTextChanged.connect(
            self._type_changed
        )

        self.geometry_combo.currentTextChanged.connect(
            self._values_changed
        )

        self.front_type_combo.currentTextChanged.connect(
            self._front_type_changed
        )

        for widget in (
            self.width_input,
            self.depth_input,
            self.width_b_input,
            self.depth_b_input,
            self.height_input,
            self.panel_input,
            self.back_input,
            self.shelf_input,
            self.plinth_height_input,
            self.plinth_setback_input,
            self.mount_height_input,
            self.x_input,
            self.y_input,
            self.z_input,
            self.rotation_input,
            self.front_thickness_input,
            self.front_gap_input,
            self.drawer_count_input,
            self.drawer_zone_height_input,
            self.corner_opening_input,
        ):
            widget.valueChanged.connect(
                self._values_changed
            )

        self.apply_mount_button.clicked.connect(
            self._apply_mount_height
        )

        close_button.clicked.connect(
            Gui.Control.closeDialog
        )

    def _load_values(
        self,
    ):
        self._updating = True

        try:
            self.info_label.setText(
                f"<b>{self.furniture.Label}</b>"
            )

            self.type_combo.setCurrentText(
                str(
                    self.furniture.CabinetType
                )
            )

            self.geometry_combo.setCurrentText(
                str(
                    self.furniture.GeometryMode
                )
            )

            self.width_input.setValue(
                self.furniture.Width.Value
            )

            self.depth_input.setValue(
                self.furniture.Depth.Value
            )

            self.width_b_input.setValue(
                self.furniture.WidthB.Value
            )

            self.depth_b_input.setValue(
                self.furniture.DepthB.Value
            )

            self.corner_opening_input.setValue(
                self.furniture.CornerOpeningWidth.Value
            )

            self.height_input.setValue(
                self.furniture.Height.Value
            )

            self.panel_input.setValue(
                self.furniture.PanelThickness.Value
            )

            self.back_input.setValue(
                self.furniture.BackThickness.Value
            )

            self.shelf_input.setValue(
                int(
                    self.furniture.ShelfCount
                )
            )

            self.plinth_height_input.setValue(
                self.furniture.PlinthHeight.Value
            )

            self.plinth_setback_input.setValue(
                self.furniture.PlinthSetback.Value
            )

            self.mount_height_input.setValue(
                self.furniture.MountHeight.Value
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

            self.front_type_combo.setCurrentText(
                str(
                    self.furniture.FrontType
                )
            )

            self.front_thickness_input.setValue(
                self.furniture.FrontThickness.Value
            )

            self.front_gap_input.setValue(
                self.furniture.FrontGap.Value
            )

            self.drawer_count_input.setValue(
                int(
                    self.furniture.DrawerCount
                )
            )

            self.drawer_zone_height_input.setValue(
                self.furniture.DrawerZoneHeight.Value
            )

        finally:
            self._updating = False

    def _update_type_ui(
        self,
    ):
        cabinet_type = (
            self.type_combo.currentText()
        )

        is_corner = (
            cabinet_type
            in {
                CABINET_CORNER_BASE,
                CABINET_CORNER_WALL,
            }
        )

        is_wall = (
            cabinet_type
            in {
                CABINET_WALL,
                CABINET_CORNER_WALL,
            }
        )

        self.corner_group.setVisible(
            is_corner
        )

        self.corner_opening_input.setEnabled(
            is_corner
        )

        self.wall_group.setVisible(
            is_wall
        )

        self.plinth_height_input.setEnabled(
            not is_wall
        )

        self.plinth_setback_input.setEnabled(
            not is_wall
        )

        self.front_group.setEnabled(
            True
        )

        self._refresh_front_type_options(
            is_corner
        )

        if is_corner:
            self.width_label.setText(
                "Width A:"
            )

            self.depth_label.setText(
                "Depth A:"
            )

        else:
            self.width_label.setText(
                "Width:"
            )

            self.depth_label.setText(
                "Depth:"
            )

    def _refresh_front_type_options(
        self,
        is_corner,
    ):
        """Show only front systems valid for the selected cabinet type."""

        current = (
            self.front_type_combo.currentText()
        )

        if is_corner:
            options = [
                FRONT_OPEN,
                FRONT_CORNER_FOLDING,
            ]
        else:
            options = [
                FRONT_OPEN,
                FRONT_SINGLE,
                FRONT_DOUBLE,
                FRONT_DRAWERS,
                FRONT_DOOR_DRAWERS,
                FRONT_LIFT_UP,
            ]

        if (
            self.front_type_combo.count()
            == len(options)
            and all(
                self.front_type_combo.itemText(i)
                == options[i]
                for i in range(
                    len(options)
                )
            )
        ):
            return

        self.front_type_combo.blockSignals(
            True
        )

        self.front_type_combo.clear()
        self.front_type_combo.addItems(
            options
        )

        if current in options:
            self.front_type_combo.setCurrentText(
                current
            )
        else:
            self.front_type_combo.setCurrentText(
                FRONT_OPEN
            )

        self.front_type_combo.blockSignals(
            False
        )

    def _update_front_ui(
        self,
    ):
        front_type = (
            self.front_type_combo.currentText()
        )

        is_drawers = (
            front_type == FRONT_DRAWERS
        )

        is_door_drawers = (
            front_type == FRONT_DOOR_DRAWERS
        )

        self.drawer_count_label.setVisible(
            is_drawers
        )

        self.drawer_count_input.setVisible(
            is_drawers
        )

        self.drawer_zone_label.setVisible(
            is_door_drawers
        )

        self.drawer_zone_height_input.setVisible(
            is_door_drawers
        )

    def _front_type_changed(
        self,
        *args,
    ):
        self._update_front_ui()
        self._values_changed()

    def _type_changed(
        self,
        *args,
    ):
        self._update_type_ui()
        self._values_changed()

    def _values_changed(
        self,
        *args,
    ):
        if self._updating:
            return

        self._updating = True

        try:
            self.furniture.CabinetType = (
                self.type_combo.currentText()
            )

            self.furniture.GeometryMode = (
                self.geometry_combo.currentText()
            )

            self.furniture.Width = (
                self.width_input.value()
            )

            self.furniture.Depth = (
                self.depth_input.value()
            )

            self.furniture.WidthB = (
                self.width_b_input.value()
            )

            self.furniture.DepthB = (
                self.depth_b_input.value()
            )

            self.furniture.CornerOpeningWidth = (
                self.corner_opening_input.value()
            )

            self.furniture.Height = (
                self.height_input.value()
            )

            self.furniture.PanelThickness = (
                self.panel_input.value()
            )

            self.furniture.BackThickness = (
                self.back_input.value()
            )

            self.furniture.ShelfCount = (
                self.shelf_input.value()
            )

            self.furniture.PlinthHeight = (
                self.plinth_height_input.value()
            )

            self.furniture.PlinthSetback = (
                self.plinth_setback_input.value()
            )

            self.furniture.MountHeight = (
                self.mount_height_input.value()
            )

            self.furniture.Position = App.Vector(
                self.x_input.value(),
                self.y_input.value(),
                self.z_input.value(),
            )

            self.furniture.RotationAngle = (
                self.rotation_input.value()
            )

            self.furniture.FrontType = (
                self.front_type_combo.currentText()
            )

            self.furniture.FrontThickness = (
                self.front_thickness_input.value()
            )

            self.furniture.FrontGap = (
                self.front_gap_input.value()
            )

            self.furniture.DrawerCount = (
                self.drawer_count_input.value()
            )

            self.furniture.DrawerZoneHeight = (
                self.drawer_zone_height_input.value()
            )

            self.furniture.Document.recompute()

        finally:
            self._updating = False

    def _apply_mount_height(
        self,
    ):
        new_z = (
            self.mount_height_input.value()
        )

        self._updating = True

        try:
            self.z_input.setValue(
                new_z
            )

            self.furniture.Position = App.Vector(
                self.furniture.Position.x,
                self.furniture.Position.y,
                new_z,
            )

            self.furniture.MountHeight = (
                new_z
            )

            self.furniture.Document.recompute()

        finally:
            self._updating = False

    def getStandardButtons(
        self,
    ):
        return 0

    def accept(
        self,
    ):
        return True

    def reject(
        self,
    ):
        return True
