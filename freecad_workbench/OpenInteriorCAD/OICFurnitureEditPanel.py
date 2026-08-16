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
    CABINET_BLIND_CORNER_BASE,
    GEOMETRY_BOX,
    GEOMETRY_CARCASS,
    FRONT_OPEN,
    FRONT_SINGLE,
    FRONT_DOUBLE,
    FRONT_DRAWERS,
    FRONT_DOOR_DRAWERS,
    FRONT_LIFT_UP,
    FRONT_CORNER_FOLDING,
    ensure_blind_corner_mate,
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
                CABINET_BLIND_CORNER_BASE,
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

        # BLIND CORNER
        self.blind_group = (
            QtWidgets.QGroupBox(
                "Blind Corner"
            )
        )

        blind_layout = (
            QtWidgets.QFormLayout(
                self.blind_group
            )
        )

        self.blind_side_combo = (
            QtWidgets.QComboBox()
        )

        self.blind_side_combo.addItems(
            [
                "Left",
                "Right",
            ]
        )

        self.blind_box_width_input = (
            self._length_spin(
                100.0,
                5000.0,
            )
        )

        self.blind_filler_width_input = (
            self._length_spin(
                0.0,
                3000.0,
            )
        )

        self.blind_door_filler_width_input = (
            self._length_spin(
                0.0,
                1000.0,
            )
        )

        self.blind_mate_width_input = (
            self._length_spin(
                100.0,
                5000.0,
            )
        )

        self.blind_mate_depth_input = (
            self._length_spin(
                100.0,
                3000.0,
            )
        )

        self.ensure_mate_button = (
            QtWidgets.QPushButton(
                "Create / Reconnect 90° Cabinet"
            )
        )

        blind_layout.addRow(
            "Hidden Side:",
            self.blind_side_combo,
        )

        blind_layout.addRow(
            "Blind Box Width:",
            self.blind_box_width_input,
        )

        blind_layout.addRow(
            "Corner Spacer Width:",
            self.blind_filler_width_input,
        )

        blind_layout.addRow(
            "Door Clearance Filler:",
            self.blind_door_filler_width_input,
        )

        blind_layout.addRow(
            "90° Cabinet Width:",
            self.blind_mate_width_input,
        )

        blind_layout.addRow(
            "90° Cabinet Depth:",
            self.blind_mate_depth_input,
        )

        blind_layout.addRow(
            self.ensure_mate_button
        )

        blind_help = QtWidgets.QLabel(
            "Corner Spacer Width is now the real physical gap between the "
            "long Blind Corner cabinet and the linked 90° cabinet. "
            "The long cabinet body/front is automatically shortened by this "
            "value. Example: Corner Depth 600 mm + Spacer 100 mm gives a "
            "500 mm deep long cabinet body and a 100 mm spacer before the "
            "90° cabinet."
        )

        blind_help.setWordWrap(
            True
        )

        blind_layout.addRow(
            blind_help
        )

        layout.addWidget(
            self.blind_group
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

        self.blind_side_combo.currentTextChanged.connect(
            self._blind_side_changed
        )

        self.ensure_mate_button.clicked.connect(
            self._ensure_blind_mate
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
            self.blind_box_width_input,
            self.blind_filler_width_input,
            self.blind_door_filler_width_input,
            self.blind_mate_width_input,
            self.blind_mate_depth_input,
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

            if "BlindSide" in self.furniture.PropertiesList:
                self.blind_side_combo.setCurrentText(
                    str(
                        self.furniture.BlindSide
                    )
                )

            if "BlindBoxWidth" in self.furniture.PropertiesList:
                self.blind_box_width_input.setValue(
                    self.furniture.BlindBoxWidth.Value
                )

            if "BlindFillerWidth" in self.furniture.PropertiesList:
                self.blind_filler_width_input.setValue(
                    self.furniture.BlindFillerWidth.Value
                )

            if "BlindDoorFillerWidth" in self.furniture.PropertiesList:
                self.blind_door_filler_width_input.setValue(
                    self.furniture.BlindDoorFillerWidth.Value
                )

            if "BlindMateWidth" in self.furniture.PropertiesList:
                self.blind_mate_width_input.setValue(
                    self.furniture.BlindMateWidth.Value
                )

            if "BlindMateDepth" in self.furniture.PropertiesList:
                self.blind_mate_depth_input.setValue(
                    self.furniture.BlindMateDepth.Value
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

        is_blind = (
            cabinet_type
            == CABINET_BLIND_CORNER_BASE
        )

        self.corner_group.setVisible(
            is_corner
        )

        self.blind_group.setVisible(
            is_blind
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

        elif is_blind:
            self.width_label.setText(
                "Overall Width:"
            )

            self.depth_label.setText(
                "Corner Depth:"
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

    def _blind_side_changed(
        self,
        *_args,
    ):
        """Mirror and resync the complete two-cabinet set in one operation."""

        if self._updating:
            return

        self._values_changed()

        if (
            self.type_combo.currentText()
            == CABINET_BLIND_CORNER_BASE
        ):
            self._ensure_blind_mate()


    def _ensure_blind_mate(
        self,
        *_args,
    ):
        if self._updating:
            return

        if self.type_combo.currentText() != CABINET_BLIND_CORNER_BASE:
            return

        # Push the currently displayed dimensions first.
        try:
            if "BlindMateWidth" in self.furniture.PropertiesList:
                self.furniture.BlindMateWidth = (
                    self.blind_mate_width_input.value()
                )

            if "BlindMateDepth" in self.furniture.PropertiesList:
                self.furniture.BlindMateDepth = (
                    self.blind_mate_depth_input.value()
                )
        except Exception:
            pass

        try:
            mate = ensure_blind_corner_mate(
                self.furniture
            )

            if mate is not None:
                self.furniture.Document.recompute()

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self.form,
                "Blind Corner",
                f"Could not create the 90° cabinet:\\n{error}",
            )


    def _type_changed(
        self,
        *args,
    ):
        if (
            not self._updating
            and self.type_combo.currentText()
            == CABINET_BLIND_CORNER_BASE
        ):
            # Switching a standard 600 mm cabinet to Blind Corner would
            # otherwise be temporarily invalid. Give it useful defaults.
            if self.width_input.value() < 900.0:
                self.width_input.setValue(
                    1200.0
                )

            if self.blind_box_width_input.value() <= 0.0:
                self.blind_box_width_input.setValue(
                    600.0
                )

            if self.blind_filler_width_input.value() <= 0.0:
                self.blind_filler_width_input.setValue(
                    100.0
                )

            if self.blind_door_filler_width_input.value() <= 0.0:
                self.blind_door_filler_width_input.setValue(
                    50.0
                )

            if self.blind_mate_width_input.value() <= 0.0:
                self.blind_mate_width_input.setValue(
                    600.0
                )

            if self.blind_mate_depth_input.value() <= 0.0:
                self.blind_mate_depth_input.setValue(
                    600.0
                )

        self._update_type_ui()
        self._values_changed()

        if (
            self.type_combo.currentText()
            == CABINET_BLIND_CORNER_BASE
        ):
            self._ensure_blind_mate()

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

            if "BlindSide" in self.furniture.PropertiesList:
                self.furniture.BlindSide = (
                    self.blind_side_combo.currentText()
                )

            if "BlindBoxWidth" in self.furniture.PropertiesList:
                self.furniture.BlindBoxWidth = (
                    self.blind_box_width_input.value()
                )

            if "BlindFillerWidth" in self.furniture.PropertiesList:
                self.furniture.BlindFillerWidth = (
                    self.blind_filler_width_input.value()
                )

            if "BlindDoorFillerWidth" in self.furniture.PropertiesList:
                self.furniture.BlindDoorFillerWidth = (
                    self.blind_door_filler_width_input.value()
                )

            if "BlindMateWidth" in self.furniture.PropertiesList:
                self.furniture.BlindMateWidth = (
                    self.blind_mate_width_input.value()
                )

            if "BlindMateDepth" in self.furniture.PropertiesList:
                self.furniture.BlindMateDepth = (
                    self.blind_mate_depth_input.value()
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
