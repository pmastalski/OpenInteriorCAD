"""Snap furniture side-to-side."""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"


def furniture_axes(
    rotation,
):
    angle = math.radians(
        rotation
    )

    x_axis = App.Vector(
        math.cos(angle),
        math.sin(angle),
        0.0,
    )

    y_axis = App.Vector(
        -math.sin(angle),
        math.cos(angle),
        0.0,
    )

    return (
        x_axis,
        y_axis,
    )


def furniture_corners(
    furniture,
):
    rotation = (
        furniture.RotationAngle.Value
    )

    x_axis, y_axis = (
        furniture_axes(
            rotation
        )
    )

    position = furniture.Position

    width = furniture.Width.Value
    depth = furniture.Depth.Value

    back_left = App.Vector(
        position.x,
        position.y,
        0.0,
    )

    back_right = App.Vector(
        position.x
        + x_axis.x * width,
        position.y
        + x_axis.y * width,
        0.0,
    )

    front_left = App.Vector(
        position.x
        + y_axis.x * depth,
        position.y
        + y_axis.y * depth,
        0.0,
    )

    front_right = App.Vector(
        back_right.x
        + y_axis.x * depth,
        back_right.y
        + y_axis.y * depth,
        0.0,
    )

    return {
        "back_left": back_left,
        "back_right": back_right,
        "front_left": front_left,
        "front_right": front_right,
    }


def edge_midpoint(
    p1,
    p2,
):
    return App.Vector(
        (
            p1.x + p2.x
        ) / 2.0,
        (
            p1.y + p2.y
        ) / 2.0,
        0.0,
    )


def get_side_midpoints(
    furniture,
):
    corners = furniture_corners(
        furniture
    )

    left_mid = edge_midpoint(
        corners["back_left"],
        corners["front_left"],
    )

    right_mid = edge_midpoint(
        corners["back_right"],
        corners["front_right"],
    )

    return (
        left_mid,
        right_mid,
    )


def snap_side_to_side(
    moving,
    target,
    click_point,
):
    """
    Moving furniture adopts target rotation.

    Click near left half of target:
        moving goes to target left side.

    Click near right half:
        moving goes to target right side.
    """

    rotation = (
        target.RotationAngle.Value
    )

    x_axis, _ = furniture_axes(
        rotation
    )

    target_position = (
        target.Position
    )

    target_width = (
        target.Width.Value
    )

    moving_width = (
        moving.Width.Value
    )

    # Determine click coordinate along target width.
    dx = (
        click_point.x
        - target_position.x
    )

    dy = (
        click_point.y
        - target_position.y
    )

    along = (
        dx * x_axis.x
        + dy * x_axis.y
    )

    # --------------------------------------------------
    # CLICK LEFT HALF:
    # moving right edge touches target left edge.
    # --------------------------------------------------

    if along < target_width / 2.0:
        position = App.Vector(
            target_position.x
            - x_axis.x
            * moving_width,
            target_position.y
            - x_axis.y
            * moving_width,
            moving.Position.z,
        )

    # --------------------------------------------------
    # CLICK RIGHT HALF:
    # moving left edge touches target right edge.
    # --------------------------------------------------

    else:
        position = App.Vector(
            target_position.x
            + x_axis.x
            * target_width,
            target_position.y
            + x_axis.y
            * target_width,
            moving.Position.z,
        )

    moving.RotationAngle = rotation
    moving.Position = position

    moving.Document.recompute()


class FurnitureSnapFurnitureTool:
    """Click target cabinet to snap selected cabinet beside it."""

    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture
        self.document = furniture.Document

        self.view = None
        self.callback = None
        self.escape_shortcut = None

        self.active = False

    def start(self):
        gui_document = Gui.activeDocument()

        if gui_document is None:
            return

        self.view = gui_document.activeView()
        self.active = True

        self.callback = self.view.addEventCallback(
            "SoMouseButtonEvent",
            self._mouse_event,
        )

        main_window = Gui.getMainWindow()

        self.escape_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Esc"),
            main_window,
        )

        self.escape_shortcut.setContext(
            QtCore.Qt.ShortcutContext.ApplicationShortcut
        )

        self.escape_shortcut.activated.connect(
            self.stop
        )

        try:
            main_window.statusBar().showMessage(
                "OpenInteriorCAD: kliknij drugą szafkę. "
                "Kliknij jej lewą lub prawą połowę, "
                "aby wybrać stronę dosunięcia. "
                "Esc = anuluj."
            )
        except Exception:
            pass

    def _mouse_event(
        self,
        info,
    ):
        if not self.active:
            return

        if info.get("State") != "DOWN":
            return

        if info.get("Button") != "BUTTON1":
            return

        object_info = self.view.getObjectInfo(
            info["Position"]
        )

        if not object_info:
            return

        object_name = object_info.get(
            "Object"
        )

        if not object_name:
            return

        target = self.document.getObject(
            object_name
        )

        if target is None:
            return

        if target == self.furniture:
            return

        if (
            getattr(
                target,
                "OICType",
                "",
            )
            != FURNITURE_TYPE
        ):
            return

        screen_position = info.get(
            "Position"
        )

        try:
            point = self.view.getPoint(
                screen_position[0],
                screen_position[1],
            )
        except Exception:
            return

        click_point = App.Vector(
            point.x,
            point.y,
            0.0,
        )

        self.document.openTransaction(
            "Dosuń mebel do szafki"
        )

        try:
            snap_side_to_side(
                self.furniture,
                target,
                click_point,
            )

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD furniture snap error: "
                f"{error}\n"
            )

            return

        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(
            self.furniture
        )

        self.stop()

    def stop(self):
        if (
            self.view is not None
            and self.callback is not None
        ):
            try:
                self.view.removeEventCallback(
                    "SoMouseButtonEvent",
                    self.callback,
                )
            except Exception:
                pass

        self.callback = None

        if self.escape_shortcut is not None:
            try:
                self.escape_shortcut.setEnabled(False)
                self.escape_shortcut.deleteLater()
            except Exception:
                pass

        self.escape_shortcut = None
        self.active = False

        try:
            Gui.getMainWindow().statusBar().clearMessage()
        except Exception:
            pass