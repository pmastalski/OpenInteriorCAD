"""Interactive front opening panel for OpenInteriorCAD.

Front Opening 0.7

Supported:
- Single Door
- Double Door
- Drawers
- Door + Drawers
- Corner Folding Doors

Standard doors rotate around the accepted clear-opening hinge line.
Corner folding fronts use a two-stage compound hinge motion.
Drawer fronts translate outward from the cabinet.
"""

from __future__ import annotations

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets


STANDARD_DOOR_FRONT_TYPES = {
    "Single Door",
    "Double Door",
}

CORNER_FRONT_TYPES = {
    "Corner Folding Doors",
}

DOOR_FRONT_TYPES = (
    STANDARD_DOOR_FRONT_TYPES
    | CORNER_FRONT_TYPES
)

DRAWER_FRONT_TYPES = {
    "Drawers",
    "Door + Drawers",
}

SUPPORTED_FRONT_TYPES = (
    DOOR_FRONT_TYPES
    | DRAWER_FRONT_TYPES
)


class FrontOpeningPanel:
    """Control doors, corner folding fronts and drawer opening."""

    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture
        self._updating = False

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Front Opening"
        )

        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            f"Cabinet: {getattr(furniture, 'Label', 'Cabinet')}"
        )
        title.setWordWrap(
            True
        )
        layout.addWidget(
            title
        )

        self.front_type_label = QtWidgets.QLabel()
        layout.addWidget(
            self.front_type_label
        )

        self.info_label = QtWidgets.QLabel()
        self.info_label.setWordWrap(
            True
        )
        layout.addWidget(
            self.info_label
        )

        # --------------------------------------------------
        # DOOR / CORNER ANGLE
        # --------------------------------------------------

        self.angle_group = QtWidgets.QGroupBox(
            "Door Opening Angle"
        )
        angle_layout = QtWidgets.QVBoxLayout(
            self.angle_group
        )

        row = QtWidgets.QHBoxLayout()

        self.angle_slider = QtWidgets.QSlider(
            QtCore.Qt.Horizontal
        )
        self.angle_slider.setRange(
            0,
            120,
        )
        self.angle_slider.setSingleStep(
            1
        )
        self.angle_slider.setPageStep(
            5
        )
        row.addWidget(
            self.angle_slider,
            1,
        )

        self.angle_spin = QtWidgets.QDoubleSpinBox()
        self.angle_spin.setRange(
            0.0,
            120.0,
        )
        self.angle_spin.setDecimals(
            1
        )
        self.angle_spin.setSingleStep(
            1.0
        )
        self.angle_spin.setSuffix(
            "°"
        )
        row.addWidget(
            self.angle_spin
        )

        angle_layout.addLayout(
            row
        )

        self.quick_angle_row = QtWidgets.QHBoxLayout()

        self.closed_button = QtWidgets.QPushButton(
            "Closed"
        )
        self.closed_button.clicked.connect(
            lambda:
                self.set_angle(
                    0
                )
        )
        self.quick_angle_row.addWidget(
            self.closed_button
        )

        self.angle45_button = QtWidgets.QPushButton(
            "45°"
        )
        self.angle45_button.clicked.connect(
            lambda:
                self.set_angle(
                    45
                )
        )
        self.quick_angle_row.addWidget(
            self.angle45_button
        )

        self.angle90_button = QtWidgets.QPushButton(
            "90°"
        )
        self.angle90_button.clicked.connect(
            lambda:
                self.set_angle(
                    90
                )
        )
        self.quick_angle_row.addWidget(
            self.angle90_button
        )

        self.angle110_button = QtWidgets.QPushButton(
            "110°"
        )
        self.angle110_button.clicked.connect(
            lambda:
                self.set_angle(
                    110
                )
        )
        self.quick_angle_row.addWidget(
            self.angle110_button
        )

        angle_layout.addLayout(
            self.quick_angle_row
        )

        layout.addWidget(
            self.angle_group
        )

        # --------------------------------------------------
        # SINGLE DOOR HINGE
        # --------------------------------------------------

        self.hinge_group = QtWidgets.QGroupBox(
            "Single Door Hinge"
        )
        hinge_layout = QtWidgets.QHBoxLayout(
            self.hinge_group
        )

        self.left_radio = QtWidgets.QRadioButton(
            "Left"
        )
        self.right_radio = QtWidgets.QRadioButton(
            "Right"
        )

        hinge_layout.addWidget(
            self.left_radio
        )
        hinge_layout.addWidget(
            self.right_radio
        )
        hinge_layout.addStretch(
            1
        )

        layout.addWidget(
            self.hinge_group
        )

        # --------------------------------------------------
        # DRAWERS
        # --------------------------------------------------

        self.drawer_group = QtWidgets.QGroupBox(
            "Drawer Opening Distance"
        )
        drawer_layout = QtWidgets.QVBoxLayout(
            self.drawer_group
        )

        row = QtWidgets.QHBoxLayout()

        self.drawer_slider = QtWidgets.QSlider(
            QtCore.Qt.Horizontal
        )
        self.drawer_slider.setRange(
            0,
            550,
        )
        self.drawer_slider.setSingleStep(
            5
        )
        self.drawer_slider.setPageStep(
            25
        )
        row.addWidget(
            self.drawer_slider,
            1,
        )

        self.drawer_spin = QtWidgets.QDoubleSpinBox()
        self.drawer_spin.setRange(
            0.0,
            550.0,
        )
        self.drawer_spin.setDecimals(
            1
        )
        self.drawer_spin.setSingleStep(
            5.0
        )
        self.drawer_spin.setSuffix(
            " mm"
        )
        row.addWidget(
            self.drawer_spin
        )

        drawer_layout.addLayout(
            row
        )

        quick = QtWidgets.QHBoxLayout()

        for distance in (
            0,
            150,
            300,
            450,
        ):
            button = QtWidgets.QPushButton(
                "Closed"
                if distance == 0
                else f"{distance} mm"
            )
            button.clicked.connect(
                lambda _checked=False, distance=distance:
                    self.set_drawer_distance(
                        distance
                    )
            )
            quick.addWidget(
                button
            )

        drawer_layout.addLayout(
            quick
        )

        layout.addWidget(
            self.drawer_group
        )

        self.status_label = QtWidgets.QLabel()
        self.status_label.setWordWrap(
            True
        )
        layout.addWidget(
            self.status_label
        )

        self.angle_slider.valueChanged.connect(
            self._angle_slider_changed
        )
        self.angle_spin.valueChanged.connect(
            self._angle_spin_changed
        )
        self.drawer_slider.valueChanged.connect(
            self._drawer_slider_changed
        )
        self.drawer_spin.valueChanged.connect(
            self._drawer_spin_changed
        )
        self.left_radio.toggled.connect(
            self._hinge_changed
        )
        self.right_radio.toggled.connect(
            self._hinge_changed
        )

        self.refresh()

    # ======================================================
    # MODEL
    # ======================================================

    def _recompute(
        self,
    ):
        try:
            self.furniture.Proxy.rebuild_geometry(
                self.furniture
            )
        except Exception:
            pass

        if App.ActiveDocument is not None:
            App.ActiveDocument.recompute()

    def _angle_limit(
        self,
    ):
        front_type = str(
            self.furniture.FrontType
        )

        if front_type in CORNER_FRONT_TYPES:
            return 90.0

        return 120.0

    def set_angle(
        self,
        angle,
    ):
        if str(
            self.furniture.FrontType
        ) not in DOOR_FRONT_TYPES:
            return

        limit = self._angle_limit()

        angle = max(
            0.0,
            min(
                limit,
                float(
                    angle
                ),
            ),
        )

        self.furniture.FrontOpenAngle = angle

        self._recompute()

        self._updating = True

        try:
            self.angle_slider.setValue(
                int(
                    round(
                        angle
                    )
                )
            )
            self.angle_spin.setValue(
                angle
            )

        finally:
            self._updating = False

        self._update_status()

    def set_drawer_distance(
        self,
        distance,
    ):
        if str(
            self.furniture.FrontType
        ) not in DRAWER_FRONT_TYPES:
            return

        distance = max(
            0.0,
            min(
                550.0,
                float(
                    distance
                ),
            ),
        )

        self.furniture.DrawerOpenDistance = distance

        self._recompute()

        self._updating = True

        try:
            self.drawer_slider.setValue(
                int(
                    round(
                        distance
                    )
                )
            )
            self.drawer_spin.setValue(
                distance
            )

        finally:
            self._updating = False

        self._update_status()

    # ======================================================
    # EVENTS
    # ======================================================

    def _angle_slider_changed(
        self,
        value,
    ):
        if not self._updating:
            self.set_angle(
                value
            )

    def _angle_spin_changed(
        self,
        value,
    ):
        if not self._updating:
            self.set_angle(
                value
            )

    def _drawer_slider_changed(
        self,
        value,
    ):
        if not self._updating:
            self.set_drawer_distance(
                value
            )

    def _drawer_spin_changed(
        self,
        value,
    ):
        if not self._updating:
            self.set_drawer_distance(
                value
            )

    def _hinge_changed(
        self,
        *_args,
    ):
        if self._updating:
            return

        if str(
            self.furniture.FrontType
        ) != "Single Door":
            return

        self.furniture.SingleDoorHingeSide = (
            "Right"
            if self.right_radio.isChecked()
            else "Left"
        )

        self._recompute()
        self._update_status()

    # ======================================================
    # UI
    # ======================================================

    def _update_status(
        self,
    ):
        front_type = str(
            self.furniture.FrontType
        )

        if front_type not in SUPPORTED_FRONT_TYPES:
            self.status_label.setText(
                f"{front_type} is not supported in Front Opening 0.7."
            )
            return

        parts = []

        if front_type in DOOR_FRONT_TYPES:
            angle = float(
                self.furniture.FrontOpenAngle.Value
            )

            if front_type in CORNER_FRONT_TYPES:
                parts.append(
                    (
                        "Corner fronts: Closed"
                        if angle <= 0.01
                        else f"Corner fronts: Folded {angle:.1f}°"
                    )
                )
            else:
                parts.append(
                    (
                        "Door: Closed"
                        if angle <= 0.01
                        else f"Door: {angle:.1f}°"
                    )
                )

            if front_type == "Single Door":
                parts.append(
                    "Hinge: "
                    + str(
                        self.furniture.SingleDoorHingeSide
                    )
                )

        if front_type in DRAWER_FRONT_TYPES:
            distance = float(
                self.furniture.DrawerOpenDistance.Value
            )

            parts.append(
                (
                    "Drawer: Closed"
                    if distance <= 0.01
                    else f"Drawer: {distance:.1f} mm"
                )
            )

        self.status_label.setText(
            " • ".join(
                parts
            )
        )

    def refresh(
        self,
    ):
        front_type = str(
            self.furniture.FrontType
        )

        self.front_type_label.setText(
            f"Front type: {front_type}"
        )

        is_corner = (
            front_type in CORNER_FRONT_TYPES
        )

        is_door = (
            front_type in DOOR_FRONT_TYPES
        )

        self.angle_group.setEnabled(
            is_door
        )

        self.hinge_group.setEnabled(
            front_type == "Single Door"
        )

        self.drawer_group.setEnabled(
            front_type in DRAWER_FRONT_TYPES
        )

        if is_corner:
            self.angle_group.setTitle(
                "Corner Folding Angle"
            )
            self.info_label.setText(
                "Corner Folding Doors use a compound motion: Leaf A rotates "
                "around the outer cabinet hinge and Leaf B folds around the "
                "moving A/B joint. Closed corner geometry is preserved."
            )

            self.angle_slider.setMaximum(
                90
            )
            self.angle_spin.setMaximum(
                90.0
            )
            self.angle110_button.setEnabled(
                False
            )

        else:
            self.angle_group.setTitle(
                "Door Opening Angle"
            )
            self.info_label.setText(
                "Doors swing outward from the clear-opening hinge line. "
                "Drawers move outward from the cabinet. "
                "Carcass and production dimensions remain unchanged."
            )

            self.angle_slider.setMaximum(
                120
            )
            self.angle_spin.setMaximum(
                120.0
            )
            self.angle110_button.setEnabled(
                True
            )

        self._updating = True

        try:
            angle = float(
                self.furniture.FrontOpenAngle.Value
            )

            angle = min(
                angle,
                self._angle_limit(),
            )

            self.angle_slider.setValue(
                int(
                    round(
                        angle
                    )
                )
            )
            self.angle_spin.setValue(
                angle
            )

            distance = float(
                self.furniture.DrawerOpenDistance.Value
            )

            self.drawer_slider.setValue(
                int(
                    round(
                        distance
                    )
                )
            )
            self.drawer_spin.setValue(
                distance
            )

            hinge_side = str(
                self.furniture.SingleDoorHingeSide
            )

            self.left_radio.setChecked(
                hinge_side != "Right"
            )
            self.right_radio.setChecked(
                hinge_side == "Right"
            )

        finally:
            self._updating = False

        self._update_status()

    # ======================================================
    # TASK PANEL
    # ======================================================

    def getStandardButtons(
        self,
    ):
        return int(
            QtWidgets.QDialogButtonBox.Close
        )

    def reject(
        self,
    ):
        Gui.Control.closeDialog()
        return True

    def accept(
        self,
    ):
        Gui.Control.closeDialog()
        return True
