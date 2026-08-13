"""Task panel for numerical OpenInteriorCAD room drawing."""

import FreeCADGui as Gui
from PySide import QtWidgets


class WallDrawingPanel:
    """FreeCAD Task Panel for numerical room drawing."""

    def __init__(self, tool):
        self.tool = tool

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Draw Room"
        )

        self._build_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Draw Room"
        )

        main_layout.addWidget(
            title
        )

        self.status_label = QtWidgets.QLabel(
            "Click the first room corner in the view."
        )

        self.status_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.status_label
        )

        # --------------------------------------------------
        # CURRENT STATE
        # --------------------------------------------------

        current_group = QtWidgets.QGroupBox(
            "Current State"
        )

        current_layout = QtWidgets.QFormLayout(
            current_group
        )

        self.wall_count_label = QtWidgets.QLabel(
            "0"
        )

        current_layout.addRow(
            "Walls:",
            self.wall_count_label,
        )

        self.heading_label = QtWidgets.QLabel(
            "—"
        )

        current_layout.addRow(
            "Direction:",
            self.heading_label,
        )

        main_layout.addWidget(
            current_group
        )

        # --------------------------------------------------
        # NEW WALL PARAMETERS
        # --------------------------------------------------

        dimensions_group = QtWidgets.QGroupBox(
            "New Wall"
        )

        dimensions_layout = QtWidgets.QFormLayout(
            dimensions_group
        )

        self.length_input = QtWidgets.QDoubleSpinBox()

        self.length_input.setRange(
            1.0,
            100000.0,
        )

        self.length_input.setDecimals(
            0
        )

        self.length_input.setValue(
            4000.0
        )

        self.length_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Length:",
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

        self.angle_input.setValue(
            0.0
        )

        self.angle_input.setSuffix(
            "°"
        )

        dimensions_layout.addRow(
            "Angle:",
            self.angle_input,
        )

        self.angle_description = QtWidgets.QLabel(
            "First wall: angle from the X axis."
        )

        self.angle_description.setWordWrap(
            True
        )

        dimensions_layout.addRow(
            self.angle_description
        )

        # --------------------------------------------------
        # QUICK ANGLES
        # --------------------------------------------------

        angle_buttons_layout = QtWidgets.QHBoxLayout()

        self.right_button = QtWidgets.QPushButton(
            "-90°"
        )

        self.straight_button = QtWidgets.QPushButton(
            "0°"
        )

        self.left_button = QtWidgets.QPushButton(
            "+90°"
        )

        self.reverse_button = QtWidgets.QPushButton(
            "180°"
        )

        angle_buttons_layout.addWidget(
            self.right_button
        )

        angle_buttons_layout.addWidget(
            self.straight_button
        )

        angle_buttons_layout.addWidget(
            self.left_button
        )

        angle_buttons_layout.addWidget(
            self.reverse_button
        )

        dimensions_layout.addRow(
            angle_buttons_layout
        )

        # --------------------------------------------------
        # THICKNESS
        # --------------------------------------------------

        self.thickness_input = QtWidgets.QDoubleSpinBox()

        self.thickness_input.setRange(
            1.0,
            5000.0,
        )

        self.thickness_input.setDecimals(
            0
        )

        self.thickness_input.setValue(
            120.0
        )

        self.thickness_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Thickness:",
            self.thickness_input,
        )

        # --------------------------------------------------
        # HEIGHT
        # --------------------------------------------------

        self.height_input = QtWidgets.QDoubleSpinBox()

        self.height_input.setRange(
            1.0,
            20000.0,
        )

        self.height_input.setDecimals(
            0
        )

        self.height_input.setValue(
            2600.0
        )

        self.height_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Height:",
            self.height_input,
        )

        main_layout.addWidget(
            dimensions_group
        )

        # --------------------------------------------------
        # ADD WALL
        # --------------------------------------------------

        self.add_wall_button = QtWidgets.QPushButton(
            "Add Wall"
        )

        self.add_wall_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.add_wall_button
        )

        # --------------------------------------------------
        # UNDO
        # --------------------------------------------------

        self.undo_wall_button = QtWidgets.QPushButton(
            "Undo Last Wall"
        )

        self.undo_wall_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.undo_wall_button
        )

        # --------------------------------------------------
        # CLOSE ROOM
        # --------------------------------------------------

        self.close_room_button = QtWidgets.QPushButton(
            "Close Room"
        )

        self.close_room_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.close_room_button
        )

        # --------------------------------------------------
        # NEW START POINT
        # --------------------------------------------------

        self.new_start_button = QtWidgets.QPushButton(
            "Pick New Start Point"
        )

        main_layout.addWidget(
            self.new_start_button
        )

        main_layout.addStretch()

        # --------------------------------------------------
        # CLOSE PANEL
        # --------------------------------------------------

        self.close_button = QtWidgets.QPushButton(
            "Close"
        )

        self.close_button.setToolTip(
            "Finish drawing and close the panel."
        )

        main_layout.addWidget(
            self.close_button
        )

        # --------------------------------------------------
        # SIGNALS
        # --------------------------------------------------

        self.right_button.clicked.connect(
            lambda: self.angle_input.setValue(
                -90.0
            )
        )

        self.straight_button.clicked.connect(
            lambda: self.angle_input.setValue(
                0.0
            )
        )

        self.left_button.clicked.connect(
            lambda: self.angle_input.setValue(
                90.0
            )
        )

        self.reverse_button.clicked.connect(
            lambda: self.angle_input.setValue(
                180.0
            )
        )

        self.add_wall_button.clicked.connect(
            self._add_wall
        )

        self.undo_wall_button.clicked.connect(
            self._undo_wall
        )

        self.close_room_button.clicked.connect(
            self._close_room
        )

        self.new_start_button.clicked.connect(
            self._request_new_start
        )

        self.close_button.clicked.connect(
            self._close_panel
        )

    # ------------------------------------------------------
    # BUTTON HANDLERS
    # ------------------------------------------------------

    def _add_wall(self):
        self.tool.add_wall(
            length=self.length_input.value(),
            relative_angle=self.angle_input.value(),
            thickness=self.thickness_input.value(),
            height=self.height_input.value(),
        )

    def _undo_wall(self):
        self.tool.undo_last_wall()

    def _close_room(self):
        self.tool.close_current_room(
            thickness=self.thickness_input.value(),
            height=self.height_input.value(),
        )

    def _request_new_start(self):
        self.tool.request_start_point()

    def _close_panel(self):
        """
        Completely finish room drawing and close
        the FreeCAD Task Panel.
        """

        self.tool.stop(
            close_panel=True
        )

    # ------------------------------------------------------
    # PANEL STATES
    # ------------------------------------------------------

    def set_start_point_ready(self):
        self.status_label.setText(
            "Start point set. "
            "Enter the first wall parameters."
        )

        self.wall_count_label.setText(
            "0"
        )

        self.heading_label.setText(
            "—"
        )

        self.add_wall_button.setEnabled(
            True
        )

        self.undo_wall_button.setEnabled(
            False
        )

        self.close_room_button.setEnabled(
            False
        )

        self.angle_input.setValue(
            0.0
        )

        self.angle_description.setText(
            "First wall: angle from the X axis."
        )

    def set_wall_added(
        self,
        wall_count,
        heading,
    ):
        self.status_label.setText(
            f"Wall {wall_count} created."
        )

        self.wall_count_label.setText(
            str(wall_count)
        )

        self.heading_label.setText(
            f"{heading:.1f}°"
        )

        self.angle_description.setText(
            "Angle from the previous wall. "
            "+90° = w lewo, -90° = w prawo."
        )

        self.undo_wall_button.setEnabled(
            True
        )

        self.close_room_button.setEnabled(
            wall_count >= 2
        )

        self.angle_input.setValue(
            90.0
        )

        self.length_input.setFocus()

        self.length_input.selectAll()

    def set_after_undo(
        self,
        wall_count,
        heading,
    ):
        self.wall_count_label.setText(
            str(wall_count)
        )

        if heading is None:
            self.heading_label.setText(
                "—"
            )

            self.angle_input.setValue(
                0.0
            )

        else:
            self.heading_label.setText(
                f"{heading:.1f}°"
            )

            self.angle_input.setValue(
                90.0
            )

        self.undo_wall_button.setEnabled(
            wall_count > 0
        )

        self.close_room_button.setEnabled(
            wall_count >= 2
        )

        self.status_label.setText(
            "The last wall was removed."
        )

    def set_room_closed(self):
        self.status_label.setText(
            "Room closed. "
            "Click the first corner "
            "of the next room."
        )

        self.wall_count_label.setText(
            "0"
        )

        self.heading_label.setText(
            "—"
        )

        self.add_wall_button.setEnabled(
            False
        )

        self.undo_wall_button.setEnabled(
            False
        )

        self.close_room_button.setEnabled(
            False
        )

        self.angle_input.setValue(
            0.0
        )

    def set_waiting_for_start(self):
        self.status_label.setText(
            "Click the first room corner in the view."
        )

        self.wall_count_label.setText(
            "0"
        )

        self.heading_label.setText(
            "—"
        )

        self.add_wall_button.setEnabled(
            False
        )

        self.undo_wall_button.setEnabled(
            False
        )

        self.close_room_button.setEnabled(
            False
        )

    # ------------------------------------------------------
    # FREECAD TASK PANEL
    # ------------------------------------------------------

    def getStandardButtons(self):
        return 0

    def accept(self):
        self.tool.stop(
            close_panel=False
        )

        return True

    def reject(self):
        self.tool.stop(
            close_panel=False
        )

        return True