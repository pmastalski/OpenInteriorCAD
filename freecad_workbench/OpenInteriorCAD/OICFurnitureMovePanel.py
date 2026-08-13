"""Precise furniture movement panel."""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICFurnitureMove import (
    FurnitureMoveTool,
)
from OICFurnitureWallOffset import (
    FurnitureWallOffsetTool,
)


class FurnitureMovePanel:
    """Precise movement and positioning panel."""

    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture

        self._updating = False

        self.free_move_tool = None
        self.wall_tool = None

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Move Furniture"
        )

        self._build_ui()
        self._load_values()

    # ==================================================
    # UI
    # ==================================================

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Move Furniture"
        )

        layout.addWidget(
            title
        )

        self.status_label = QtWidgets.QLabel(
            ""
        )

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        # ==================================================
        # POSITION
        # ==================================================

        position_group = QtWidgets.QGroupBox(
            "Position"
        )

        position_layout = QtWidgets.QFormLayout(
            position_group
        )

        self.x_input = self._position_spin()
        self.y_input = self._position_spin()
        self.z_input = self._position_spin()

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

        # ==================================================
        # NUDGE
        # ==================================================

        nudge_group = QtWidgets.QGroupBox(
            "Nudge"
        )

        nudge_layout = QtWidgets.QVBoxLayout(
            nudge_group
        )

        step_layout = QtWidgets.QFormLayout()

        self.step_input = (
            QtWidgets.QDoubleSpinBox()
        )

        self.step_input.setRange(
            0.1,
            10000.0,
        )

        self.step_input.setDecimals(
            1
        )

        self.step_input.setValue(
            10.0
        )

        self.step_input.setSuffix(
            " mm"
        )

        step_layout.addRow(
            "Step:",
            self.step_input,
        )

        nudge_layout.addLayout(
            step_layout
        )

        direction_grid = (
            QtWidgets.QGridLayout()
        )

        self.forward_button = (
            QtWidgets.QPushButton(
                "↑ Forward"
            )
        )

        self.left_button = (
            QtWidgets.QPushButton(
                "← Left"
            )
        )

        self.right_button = (
            QtWidgets.QPushButton(
                "Right →"
            )
        )

        self.back_button = (
            QtWidgets.QPushButton(
                "↓ Back"
            )
        )

        direction_grid.addWidget(
            self.forward_button,
            0,
            1,
        )

        direction_grid.addWidget(
            self.left_button,
            1,
            0,
        )

        direction_grid.addWidget(
            self.right_button,
            1,
            2,
        )

        direction_grid.addWidget(
            self.back_button,
            2,
            1,
        )

        nudge_layout.addLayout(
            direction_grid
        )

        quick_label = QtWidgets.QLabel(
            "Quick Step"
        )

        nudge_layout.addWidget(
            quick_label
        )

        quick_layout = QtWidgets.QHBoxLayout()

        for value in [
            1,
            5,
            10,
            50,
            100,
        ]:
            button = QtWidgets.QPushButton(
                str(value)
            )

            button.clicked.connect(
                lambda checked=False, v=value:
                self.step_input.setValue(v)
            )

            quick_layout.addWidget(
                button
            )

        nudge_layout.addLayout(
            quick_layout
        )

        layout.addWidget(
            nudge_group
        )

        # ==================================================
        # ROTATE
        # ==================================================

        rotate_group = QtWidgets.QGroupBox(
            "Rotate"
        )

        rotate_layout = QtWidgets.QVBoxLayout(
            rotate_group
        )

        angle_form = QtWidgets.QFormLayout()

        self.angle_step_input = (
            QtWidgets.QDoubleSpinBox()
        )

        self.angle_step_input.setRange(
            0.1,
            360.0,
        )

        self.angle_step_input.setDecimals(
            1
        )

        self.angle_step_input.setValue(
            5.0
        )

        self.angle_step_input.setSuffix(
            "°"
        )

        angle_form.addRow(
            "Angle Step:",
            self.angle_step_input,
        )

        rotate_layout.addLayout(
            angle_form
        )

        rotate_buttons = (
            QtWidgets.QHBoxLayout()
        )

        self.rotate_left_button = (
            QtWidgets.QPushButton(
                "↺ Left"
            )
        )

        self.rotate_right_button = (
            QtWidgets.QPushButton(
                "Right ↻"
            )
        )

        rotate_buttons.addWidget(
            self.rotate_left_button
        )

        rotate_buttons.addWidget(
            self.rotate_right_button
        )

        rotate_layout.addLayout(
            rotate_buttons
        )

        quick_angle_label = QtWidgets.QLabel(
            "Quick Angle"
        )

        rotate_layout.addWidget(
            quick_angle_label
        )

        quick_angle_layout = (
            QtWidgets.QHBoxLayout()
        )

        for value in [
            1,
            5,
            15,
            45,
            90,
        ]:
            button = QtWidgets.QPushButton(
                f"{value}°"
            )

            button.clicked.connect(
                lambda checked=False, v=value:
                self.angle_step_input.setValue(v)
            )

            quick_angle_layout.addWidget(
                button
            )

        rotate_layout.addLayout(
            quick_angle_layout
        )

        layout.addWidget(
            rotate_group
        )

        # ==================================================
        # WALL OFFSET
        # ==================================================

        wall_group = QtWidgets.QGroupBox(
            "Wall Offset"
        )

        wall_layout = QtWidgets.QFormLayout(
            wall_group
        )

        self.wall_offset_input = (
            QtWidgets.QDoubleSpinBox()
        )

        self.wall_offset_input.setRange(
            0.0,
            10000.0,
        )

        self.wall_offset_input.setDecimals(
            1
        )

        self.wall_offset_input.setValue(
            0.0
        )

        self.wall_offset_input.setSuffix(
            " mm"
        )

        wall_layout.addRow(
            "Offset:",
            self.wall_offset_input,
        )

        self.set_from_wall_button = (
            QtWidgets.QPushButton(
                "Set Wall Offset"
            )
        )

        wall_layout.addRow(
            self.set_from_wall_button
        )

        layout.addWidget(
            wall_group
        )

        # ==================================================
        # FREE MOVE
        # ==================================================

        self.free_move_button = (
            QtWidgets.QPushButton(
                "Free Move"
            )
        )

        layout.addWidget(
            self.free_move_button
        )

        self.close_button = (
            QtWidgets.QPushButton(
                "Close"
            )
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        # ==================================================
        # SIGNALS
        # ==================================================

        self.x_input.valueChanged.connect(
            self._position_changed
        )

        self.y_input.valueChanged.connect(
            self._position_changed
        )

        self.z_input.valueChanged.connect(
            self._position_changed
        )

        self.rotation_input.valueChanged.connect(
            self._position_changed
        )

        self.left_button.clicked.connect(
            self._move_left
        )

        self.right_button.clicked.connect(
            self._move_right
        )

        self.forward_button.clicked.connect(
            self._move_forward
        )

        self.back_button.clicked.connect(
            self._move_back
        )

        self.rotate_left_button.clicked.connect(
            self._rotate_left
        )

        self.rotate_right_button.clicked.connect(
            self._rotate_right
        )

        self.set_from_wall_button.clicked.connect(
            self._set_from_wall
        )

        self.free_move_button.clicked.connect(
            self._free_move
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _position_spin(self):
        spin = QtWidgets.QDoubleSpinBox()

        spin.setRange(
            -1000000.0,
            1000000.0,
        )

        spin.setDecimals(
            1
        )

        spin.setSuffix(
            " mm"
        )

        return spin

    # ==================================================
    # LOAD / REFRESH
    # ==================================================

    def _load_values(self):
        self._updating = True

        try:
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

            self.status_label.setText(
                f"<b>{self.furniture.Label}</b>"
            )

        finally:
            self._updating = False

    def refresh(self):
        self._load_values()

        try:
            Gui.activeDocument().activeView().redraw()
        except Exception:
            pass

    # ==================================================
    # DIRECT POSITION
    # ==================================================

    def _position_changed(
        self,
        *args,
    ):
        if self._updating:
            return

        self.furniture.Position = App.Vector(
            self.x_input.value(),
            self.y_input.value(),
            self.z_input.value(),
        )

        self.furniture.RotationAngle = (
            self.rotation_input.value()
        )

        self.furniture.Document.recompute()

    # ==================================================
    # LOCAL AXES
    # ==================================================

    def _local_axes(self):
        angle = math.radians(
            self.furniture.RotationAngle.Value
        )

        local_x = App.Vector(
            math.cos(angle),
            math.sin(angle),
            0.0,
        )

        local_y = App.Vector(
            -math.sin(angle),
            math.cos(angle),
            0.0,
        )

        return (
            local_x,
            local_y,
        )

    # ==================================================
    # NUDGE
    # ==================================================

    def _nudge(
        self,
        dx,
        dy,
    ):
        step = (
            self.step_input.value()
        )

        local_x, local_y = (
            self._local_axes()
        )

        movement = App.Vector(
            local_x.x * dx * step
            + local_y.x * dy * step,
            local_x.y * dx * step
            + local_y.y * dy * step,
            0.0,
        )

        self.furniture.Document.openTransaction(
            "Nudge Furniture"
        )

        try:
            self.furniture.Position = App.Vector(
                self.furniture.Position.x
                + movement.x,
                self.furniture.Position.y
                + movement.y,
                self.furniture.Position.z,
            )

            self.furniture.Document.recompute()

            self.furniture.Document.commitTransaction()

        except Exception:
            self.furniture.Document.abortTransaction()
            raise

        self.refresh()

    def _move_left(self):
        self._nudge(
            -1.0,
            0.0,
        )

    def _move_right(self):
        self._nudge(
            1.0,
            0.0,
        )

    def _move_forward(self):
        self._nudge(
            0.0,
            1.0,
        )

    def _move_back(self):
        self._nudge(
            0.0,
            -1.0,
        )

    # ==================================================
    # ROTATION AROUND CENTRE
    # ==================================================

    def _furniture_centre(self):
        """
        Return the current footprint centre
        of the furniture.
        """

        angle = math.radians(
            self.furniture.RotationAngle.Value
        )

        local_x = App.Vector(
            math.cos(angle),
            math.sin(angle),
            0.0,
        )

        local_y = App.Vector(
            -math.sin(angle),
            math.cos(angle),
            0.0,
        )

        half_width = (
            self.furniture.Width.Value
            / 2.0
        )

        half_depth = (
            self.furniture.Depth.Value
            / 2.0
        )

        return App.Vector(
            self.furniture.Position.x
            + local_x.x * half_width
            + local_y.x * half_depth,

            self.furniture.Position.y
            + local_x.y * half_width
            + local_y.y * half_depth,

            self.furniture.Position.z,
        )

    def _rotate_about_centre(
        self,
        delta_angle,
    ):
        """
        Rotate furniture while keeping its
        footprint centre fixed.
        """

        centre = (
            self._furniture_centre()
        )

        current_rotation = (
            self.furniture.RotationAngle.Value
        )

        new_rotation = (
            current_rotation
            + delta_angle
        )

        new_rotation = (
            new_rotation + 180.0
        ) % 360.0 - 180.0

        angle = math.radians(
            new_rotation
        )

        local_x = App.Vector(
            math.cos(angle),
            math.sin(angle),
            0.0,
        )

        local_y = App.Vector(
            -math.sin(angle),
            math.cos(angle),
            0.0,
        )

        half_width = (
            self.furniture.Width.Value
            / 2.0
        )

        half_depth = (
            self.furniture.Depth.Value
            / 2.0
        )

        new_position = App.Vector(
            centre.x
            - local_x.x * half_width
            - local_y.x * half_depth,

            centre.y
            - local_x.y * half_width
            - local_y.y * half_depth,

            self.furniture.Position.z,
        )

        self.furniture.Document.openTransaction(
            "Rotate Furniture"
        )

        try:
            self.furniture.RotationAngle = (
                new_rotation
            )

            self.furniture.Position = (
                new_position
            )

            self.furniture.Document.recompute()

            self.furniture.Document.commitTransaction()

        except Exception:
            self.furniture.Document.abortTransaction()
            raise

        self.refresh()

    def _rotate_left(self):
        step = (
            self.angle_step_input.value()
        )

        self._rotate_about_centre(
            step
        )

    def _rotate_right(self):
        step = (
            self.angle_step_input.value()
        )

        self._rotate_about_centre(
            -step
        )

    # ==================================================
    # WALL OFFSET
    # ==================================================

    def _set_from_wall(self):
        """Set exact clearance from selected wall."""

        if (
            self.wall_tool is not None
            and self.wall_tool.active
        ):
            self.wall_tool.stop()

        offset = (
            self.wall_offset_input.value()
        )

        self.wall_tool = (
            FurnitureWallOffsetTool(
                furniture=self.furniture,
                offset=offset,
                on_finished=self._wall_finished,
            )
        )

        self.wall_tool.start()

        self.status_label.setText(
            "Select reference wall..."
        )

    def _wall_finished(self):
        self.refresh()

        self.status_label.setText(
            "Wall offset applied."
        )

    # ==================================================
    # FREE MOVE
    # ==================================================

    def _free_move(self):
        if (
            self.free_move_tool is not None
            and self.free_move_tool.active
        ):
            self.free_move_tool.stop()

        self.free_move_tool = (
            FurnitureMoveTool(
                furniture=self.furniture,
                on_finished=self._free_move_finished,
                on_cancelled=self.refresh,
            )
        )

        self.free_move_tool.start()

        self.status_label.setText(
            "Free Move active..."
        )

    def _free_move_finished(self):
        self.refresh()

        self.status_label.setText(
            "Position updated."
        )

    # ==================================================
    # CLOSE
    # ==================================================

    def _close(self):
        if (
            self.free_move_tool is not None
            and self.free_move_tool.active
        ):
            self.free_move_tool.stop()

        if (
            self.wall_tool is not None
            and self.wall_tool.active
        ):
            self.wall_tool.stop()

        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True