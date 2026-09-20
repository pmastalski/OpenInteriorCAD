"""Edit panel for the universal OpenInteriorCAD Cabinet."""

import json
from OICTallZones import ZONE_TYPES, example_zones, decode, layout as tall_zone_layout, front_bounds as tall_front_bounds
from OICDrawerLayout import heights as resolve_drawers, decode as decode_drawers, auto_index as drawer_auto_index, MIN_FRONT

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
        self._drawer_custom = decode_drawers(
            str(getattr(furniture, "DrawerHeightsJSON", "[]"))
        )

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

        # TALL CABINET — independent compartments from bottom to top.
        self.tall_group = QtWidgets.QGroupBox("Tall Cabinet - Independent Zones")
        tall_layout = QtWidgets.QVBoxLayout(self.tall_group)
        tall_layout.addWidget(QtWidgets.QLabel(
            "Bottom to top. Height = clear compartment height (mm); "
            "0 = remaining height. Oven/Microwave are empty niches."
        ))
        self.tall_table = QtWidgets.QTableWidget(0, 3)
        self.tall_table.setHorizontalHeaderLabels(
            ["Zone type", "Clear height (mm)", "Drawers"]
        )
        self.tall_table.horizontalHeader().setStretchLastSection(True)
        self.tall_table.setMinimumHeight(190)
        tall_layout.addWidget(self.tall_table)
        tall_buttons = QtWidgets.QHBoxLayout()
        self.tall_example_button = QtWidgets.QPushButton("Example: oven + microwave")
        self.tall_add_button = QtWidgets.QPushButton("Add zone")
        self.tall_remove_button = QtWidgets.QPushButton("Remove")
        self.tall_up_button = QtWidgets.QPushButton("Up")
        self.tall_down_button = QtWidgets.QPushButton("Down")
        self.tall_auto_button = QtWidgets.QPushButton("Auto Height")
        self.tall_drawer_button = QtWidgets.QPushButton("Drawer heights...")
        for button in (self.tall_example_button, self.tall_add_button,
                       self.tall_remove_button, self.tall_up_button,
                       self.tall_down_button, self.tall_auto_button,
                       self.tall_drawer_button):
            tall_buttons.addWidget(button)
        tall_layout.addLayout(tall_buttons)
        self.tall_status = QtWidgets.QLabel("")
        tall_layout.addWidget(self.tall_status)
        layout.addWidget(self.tall_group)

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

        self.extended_sides_combo = QtWidgets.QComboBox()
        self.extended_sides_combo.addItems(["None", "Left", "Right", "Both"])
        self.extended_sides_label = QtWidgets.QLabel("Floor-reaching Sides:")
        carcass_layout.addRow(self.extended_sides_label, self.extended_sides_combo)

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
        self.front_gap_input.setToolTip(
            "Global clear gap: full value between drawers / door leaves "
            "and at the top and bottom; half on the left and right "
            "outer edges. Example: 2 mm = 2 mm between fronts, "
            "1 mm at either side."
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

        self.wall_front_drop_input = self._length_spin(0.0, 500.0)
        self.wall_front_drop_label = QtWidgets.QLabel("Front Drop Below Cabinet:")
        front_layout.addRow(self.wall_front_drop_label, self.wall_front_drop_input)

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

        self.drawer_division_button = QtWidgets.QPushButton("Set individual heights...")
        front_layout.addRow(self.drawer_division_button)

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

        self.tall_example_button.clicked.connect(self._tall_example)
        self.tall_add_button.clicked.connect(self._tall_add)
        self.tall_remove_button.clicked.connect(self._tall_remove)
        self.tall_up_button.clicked.connect(lambda: self._tall_move(-1))
        self.tall_down_button.clicked.connect(lambda: self._tall_move(1))
        self.tall_auto_button.clicked.connect(self._tall_auto_height)
        self.tall_drawer_button.clicked.connect(self._edit_tall_drawers)
        self.extended_sides_combo.currentTextChanged.connect(self._values_changed)

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
            self.wall_front_drop_input,
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

        self.drawer_division_button.clicked.connect(self._edit_standard_drawers)

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
            self.wall_front_drop_input.setValue(float(getattr(self.furniture, "WallFrontDrop", 0.0)))
            self.extended_sides_combo.setCurrentText(str(getattr(self.furniture, "ExtendedSides", "None")))

            self.drawer_count_input.setValue(
                int(
                    self.furniture.DrawerCount
                )
            )

            self.drawer_zone_height_input.setValue(
                self.furniture.DrawerZoneHeight.Value
            )

            self._tall_fill(decode(str(getattr(self.furniture, "TallZonesJSON", ""))))

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

        self.tall_group.setVisible(cabinet_type == CABINET_TALL)
        can_extend = cabinet_type in (CABINET_BASE, CABINET_TALL)
        self.extended_sides_combo.setVisible(can_extend)
        self.extended_sides_label.setVisible(can_extend)
        self.wall_front_drop_input.setVisible(cabinet_type == CABINET_WALL)
        self.wall_front_drop_label.setVisible(cabinet_type == CABINET_WALL)

        self.wall_group.setVisible(
            is_wall
        )

        self.plinth_height_input.setEnabled(
            not is_wall
        )

        self.plinth_setback_input.setEnabled(
            not is_wall
        )

        self.front_group.setEnabled(True)

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
        self.drawer_division_button.setVisible(is_drawers)

    def _drawer_dialog(self, total, count, gap, current, title):
        """Edit any n-1 heights, select any one drawer as the auto remainder.

        Front order is bottom-to-top. A radio button determines which front is
        calculated, so the automatic height is NOT tied to the last/top row.
        """
        initial = resolve_drawers(total, count, gap, current)
        if not initial:
            QtWidgets.QMessageBox.warning(
                self.form, title,
                "Not enough available front height for this number of drawers "
                "and the selected Front Gap. Check cabinet/zone dimensions.",
            )
            return None

        auto = drawer_auto_index(current, count)
        dialog = QtWidgets.QDialog(self.form)
        dialog.setWindowTitle(title)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(QtWidgets.QLabel(
            "Drawer fronts from BOTTOM to TOP (mm). Select 'Auto' beside any "
            "drawer; its height fills the exact remaining space. "
            "The Front Gap is deducted automatically."
        ))

        fields = []
        auto_buttons = []
        group = QtWidgets.QButtonGroup(dialog)
        group.setExclusive(True)
        for i, h in enumerate(initial):
            line = QtWidgets.QHBoxLayout()
            line.addWidget(QtWidgets.QLabel("Drawer {:02d}:".format(i + 1)))
            spin = self._length_spin(MIN_FRONT, max(MIN_FRONT, total), decimals=2)
            spin.setValue(h)
            fields.append(spin)
            line.addWidget(spin)
            radio = QtWidgets.QRadioButton("Auto")
            group.addButton(radio, i)
            radio.setChecked(i == auto)
            auto_buttons.append(radio)
            line.addWidget(radio)
            layout.addLayout(line)

        info = QtWidgets.QLabel("")
        info.setWordWrap(True)
        layout.addWidget(info)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        layout.addWidget(buttons)
        ok_button = buttons.button(QtWidgets.QDialogButtonBox.Ok)
        usable = total - gap * (count - 1)

        def sync(*_):
            chosen = group.checkedId()
            if chosen < 0:
                return
            remainder = usable - sum(
                field.value() for index, field in enumerate(fields)
                if index != chosen
            )
            valid = MIN_FRONT - 0.001 <= remainder <= fields[chosen].maximum() + 0.001
            fields[chosen].blockSignals(True)
            fields[chosen].setValue(max(MIN_FRONT, min(fields[chosen].maximum(), remainder)))
            fields[chosen].blockSignals(False)
            for index, field in enumerate(fields):
                is_auto = index == chosen
                field.setReadOnly(is_auto)
                field.setButtonSymbols(
                    QtWidgets.QAbstractSpinBox.NoButtons if is_auto
                    else QtWidgets.QAbstractSpinBox.UpDownArrows
                )
                field.setToolTip(
                    "Calculated automatically from the other drawer heights."
                    if is_auto else "Enter this drawer front height in mm."
                )
            info.setText(
                "Front envelope: {:.2f} mm | internal gaps: {:.2f} mm | "
                "Drawer {:02d} (Auto): {:.2f} mm".format(
                    total, gap * (count - 1), chosen + 1, remainder,
                ) if valid else
                "Not enough space: reduce the entered heights to leave at "
                "least {:.1f} mm for Drawer {:02d}.".format(MIN_FRONT, chosen + 1)
            )
            ok_button.setEnabled(valid)

        for field in fields:
            field.valueChanged.connect(sync)
        for radio in auto_buttons:
            radio.toggled.connect(sync)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        sync()
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return None
        chosen = group.checkedId()
        return [None if index == chosen else field.value()
                for index, field in enumerate(fields)]

    def _edit_standard_drawers(self):
        count = self.drawer_count_input.value()
        total = (self.height_input.value()
                 - (self.plinth_height_input.value()
                    if self.type_combo.currentText() != CABINET_WALL else 0.0)
                 - 2.0 * self.front_gap_input.value())
        if self.type_combo.currentText() == CABINET_WALL:
            total += self.wall_front_drop_input.value()
        values = self._drawer_dialog(
            total, count, self.front_gap_input.value(),
            self._drawer_custom, "Drawer front heights",
        )
        if values is not None:
            self._drawer_custom = values
            self._values_changed()

    def _edit_tall_drawers(self):
        index = self.tall_table.currentRow()
        rows = self._tall_read()
        if index < 0 or index >= len(rows) or rows[index]["type"] != "Drawers":
            QtWidgets.QMessageBox.information(
                self.form, "Drawer heights", "Select a Drawers zone first."
            )
            return
        zones = tall_zone_layout(
            json.dumps(rows), self.height_input.value(),
            self.plinth_height_input.value(), self.panel_input.value(),
        )
        if not zones:
            QtWidgets.QMessageBox.warning(
                self.form, "Drawer heights", "Correct the tall-zone heights first."
            )
            return
        _start, total = tall_front_bounds(
            zones, index, self.panel_input.value(), self.front_gap_input.value(),
        )
        values = self._drawer_dialog(
            total, rows[index]["drawers"], self.front_gap_input.value(),
            rows[index].get("drawer_heights", []),
            "Zone {:02d} drawer front heights".format(index + 1),
        )
        if values is not None:
            rows[index]["drawer_heights"] = values
            self._tall_fill(rows)
            self.tall_table.selectRow(index)
            self._values_changed()

    def _tall_read(self):
        rows = []
        for i in range(self.tall_table.rowCount()):
            rows.append({
                "type": self.tall_table.cellWidget(i, 0).currentText(),
                "height": self.tall_table.cellWidget(i, 1).value(),
                "drawers": self.tall_table.cellWidget(i, 2).value(),
                "drawer_heights": (
                    self.tall_table.cellWidget(i, 2).property("oic_heights") or []
                ),
            })
        return rows

    def _tall_fill(self, rows):
        self._updating = True
        try:
            self.tall_table.setRowCount(0)
            for row in rows:
                i = self.tall_table.rowCount()
                self.tall_table.insertRow(i)
                kind = QtWidgets.QComboBox()
                kind.addItems(ZONE_TYPES)
                kind.setCurrentText(row["type"])
                height = self._length_spin(0, 10000)
                height.setValue(row["height"])
                drawers = QtWidgets.QSpinBox()
                drawers.setRange(1, 12)
                drawers.setValue(row["drawers"])
                drawers.setProperty("oic_heights", row.get("drawer_heights", []))
                self.tall_table.setCellWidget(i, 0, kind)
                self.tall_table.setCellWidget(i, 1, height)
                self.tall_table.setCellWidget(i, 2, drawers)
                kind.currentTextChanged.connect(self._tall_changed)
                height.valueChanged.connect(self._tall_changed)
                drawers.valueChanged.connect(self._tall_changed)
        finally:
            self._updating = False
        self._tall_status_update()

    def _tall_status_update(self):
        rows = self._tall_read()
        if not rows:
            self.tall_status.setText("No zones: legacy Tall cabinet layout.")
            return
        raw = json.dumps(rows)
        zones = tall_zone_layout(
            raw, self.height_input.value(), self.plinth_height_input.value(),
            self.panel_input.value(),
        )
        if not zones:
            self.tall_status.setText(
                "INVALID: total clear heights + partitions must equal "
                "available space. Use one 0 mm row for automatic remainder."
            )
        else:
            self.tall_status.setText(
                "OK: {} zones, {} internal dividers. Auto height: {} mm".format(
                    len(zones), len(zones)-1,
                    round(next((h for r, z, h in zones if r["height"] == 0), 0), 1),
                )
            )

    def _tall_changed(self, *_args):
        if self._updating:
            return
        self._tall_status_update()
        self._values_changed()

    def _tall_example(self):
        self._tall_fill(example_zones())
        self._values_changed()

    def _tall_add(self):
        rows = self._tall_read()
        rows.append({"type": "Single Door", "height": 0 if not any(
            r["height"] == 0 for r in rows) else 300, "drawers": 1})
        self._tall_fill(rows)
        self._values_changed()

    def _tall_auto_height(self):
        """Write the calculated remaining clear height into the last zone.

        Height 0 remains supported by the zone engine as an automatic value,
        but the button must fill the visible spin box with the actual number.
        """
        rows = self._tall_read()
        if not rows:
            self.tall_status.setText("Add a zone before using Auto Height.")
            return

        # Auto Height fills the LAST height field, as opposed to merely
        # storing the sentinel 0 (which looks like a broken UI).
        index = len(rows) - 1
        old_layout = tall_zone_layout(
            json.dumps(rows), self.height_input.value(),
            self.plinth_height_input.value(), self.panel_input.value(),
        )

        # If another zone was formerly automatic, freeze its currently
        # calculated height before calculating the last zone.
        for i, row in enumerate(rows):
            if i != index and row["height"] == 0.0:
                if not old_layout:
                    self.tall_status.setText(
                        "Set the height of the other automatic zone first."
                    )
                    return
                row["height"] = old_layout[i][2]

        thickness = self.panel_input.value()
        usable = (
            self.height_input.value()
            - self.plinth_height_input.value()
            - 2.0 * thickness
            - (len(rows) - 1) * thickness
        )
        remaining = usable - sum(
            row["height"] for i, row in enumerate(rows) if i != index
        )
        if remaining < 40.0:
            self.tall_status.setText(
                "Cannot fill last zone: remaining clear height is "
                f"{remaining:.1f} mm (minimum 40 mm)."
            )
            return

        # QDoubleSpinBox keeps the same decimal precision as manually typed
        # values. The last zone is now an explicit editable dimension.
        rows[index]["height"] = round(remaining, 1)
        self._tall_fill(rows)
        self.tall_table.selectRow(index)
        self._values_changed()

    def _tall_remove(self):
        row = self.tall_table.currentRow()
        if row < 0:
            return
        rows = self._tall_read()
        rows.pop(row)
        self._tall_fill(rows)
        self._values_changed()

    def _tall_move(self, step):
        i = self.tall_table.currentRow()
        rows = self._tall_read()
        j = i + step
        if not (0 <= i < len(rows) and 0 <= j < len(rows)):
            return
        rows[i], rows[j] = rows[j], rows[i]
        self._tall_fill(rows)
        self.tall_table.selectRow(j)
        self._values_changed()

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
        if not self._updating and self.type_combo.currentText() == CABINET_TALL:
            # An ordinary 850 mm base cabinet cannot contain the example's
            # clear oven + microwave niches. Seed useful Tall dimensions.
            if self.height_input.value() < 1750.0:
                self.height_input.setValue(2200.0)
            if not self._tall_read():
                self._tall_fill(example_zones())

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
            self.furniture.WallFrontDrop = self.wall_front_drop_input.value()
            self.furniture.ExtendedSides = self.extended_sides_combo.currentText()

            if "DrawerHeightsJSON" in self.furniture.PropertiesList:
                self.furniture.DrawerHeightsJSON = json.dumps(self._drawer_custom)

            self.furniture.DrawerCount = (
                self.drawer_count_input.value()
            )

            self.furniture.DrawerZoneHeight = (
                self.drawer_zone_height_input.value()
            )

            if "TallZonesJSON" in self.furniture.PropertiesList:
                self.furniture.TallZonesJSON = json.dumps(self._tall_read())

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
