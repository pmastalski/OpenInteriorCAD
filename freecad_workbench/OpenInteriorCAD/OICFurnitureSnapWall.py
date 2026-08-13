"""Snap furniture back edge to a selected wall."""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui


WALL_TYPE = "OpenInteriorCAD::Wall"

REFERENCE_AXIS = "Oś"
REFERENCE_LEFT = "Lewa krawędź"
REFERENCE_RIGHT = "Prawa krawędź"


def normalize_angle(angle):
    """Normalize angle to -180..180."""

    return (
        angle + 180.0
    ) % 360.0 - 180.0


def wall_unit_vectors(wall):
    """Return wall tangent and left normal."""

    dx = (
        wall.EndPoint.x
        - wall.StartPoint.x
    )

    dy = (
        wall.EndPoint.y
        - wall.StartPoint.y
    )

    length = math.hypot(
        dx,
        dy,
    )

    if length <= 0.001:
        return (
            App.Vector(
                1.0,
                0.0,
                0.0,
            ),
            App.Vector(
                0.0,
                1.0,
                0.0,
            ),
        )

    tangent = App.Vector(
        dx / length,
        dy / length,
        0.0,
    )

    normal = App.Vector(
        -tangent.y,
        tangent.x,
        0.0,
    )

    return (
        tangent,
        normal,
    )


def wall_face_offsets(wall):
    """Return offsets of both physical wall faces."""

    thickness = (
        wall.Thickness.Value
    )

    reference = str(
        wall.ReferenceLine
    )

    if reference == REFERENCE_AXIS:
        return (
            thickness / 2.0,
            -thickness / 2.0,
        )

    if reference == REFERENCE_LEFT:
        return (
            thickness,
            0.0,
        )

    if reference == REFERENCE_RIGHT:
        return (
            0.0,
            -thickness,
        )

    return (
        thickness / 2.0,
        -thickness / 2.0,
    )


def point_to_segment(
    point,
    start,
    end,
):
    """Return closest point, distance and segment parameter."""

    vx = end.x - start.x
    vy = end.y - start.y

    wx = point.x - start.x
    wy = point.y - start.y

    length_squared = (
        vx * vx
        + vy * vy
    )

    if length_squared <= 0.001:
        closest = App.Vector(
            start.x,
            start.y,
            0.0,
        )

        distance = math.hypot(
            point.x - start.x,
            point.y - start.y,
        )

        return (
            closest,
            distance,
            0.0,
        )

    t = (
        wx * vx
        + wy * vy
    ) / length_squared

    t = max(
        0.0,
        min(
            1.0,
            t,
        ),
    )

    closest = App.Vector(
        start.x + vx * t,
        start.y + vy * t,
        0.0,
    )

    distance = math.hypot(
        point.x - closest.x,
        point.y - closest.y,
    )

    return (
        closest,
        distance,
        t,
    )


def make_wall_face_segment(
    wall,
    offset,
):
    """Return start/end of one real wall face."""

    _, normal = wall_unit_vectors(
        wall
    )

    start = App.Vector(
        wall.StartPoint.x
        + normal.x * offset,
        wall.StartPoint.y
        + normal.y * offset,
        0.0,
    )

    end = App.Vector(
        wall.EndPoint.x
        + normal.x * offset,
        wall.EndPoint.y
        + normal.y * offset,
        0.0,
    )

    return (
        start,
        end,
    )


def get_selected_face(
    wall,
    click_point,
):
    """
    Return the physical wall face nearest
    to the clicked point.
    """

    positive_offset, negative_offset = (
        wall_face_offsets(
            wall
        )
    )

    candidates = []

    for side, offset in (
        (1.0, positive_offset),
        (-1.0, negative_offset),
    ):
        start, end = (
            make_wall_face_segment(
                wall,
                offset,
            )
        )

        (
            closest,
            distance,
            t,
        ) = point_to_segment(
            click_point,
            start,
            end,
        )

        candidates.append(
            (
                distance,
                side,
                offset,
                closest,
                t,
            )
        )

    candidates.sort(
        key=lambda value: value[0]
    )

    return candidates[0]


def rotation_for_wall(
    wall,
    side,
):
    """
    Return furniture rotation so local +Y
    points away from selected wall face.
    """

    _, normal = wall_unit_vectors(
        wall
    )

    front_x = (
        normal.x * side
    )

    front_y = (
        normal.y * side
    )

    rotation = math.degrees(
        math.atan2(
            -front_x,
            front_y,
        )
    )

    return normalize_angle(
        rotation
    )


def snap_to_wall(
    furniture,
    wall,
    click_point,
):
    """
    Place furniture with its back edge
    directly against selected wall face.

    Click position determines location along wall.
    """

    tangent, normal = (
        wall_unit_vectors(
            wall
        )
    )

    (
        _distance,
        side,
        face_offset,
        face_point,
        _t,
    ) = get_selected_face(
        wall,
        click_point,
    )

    width = (
        furniture.Width.Value
    )

    half_width = (
        width / 2.0
    )

    dx = (
        face_point.x
        - wall.StartPoint.x
    )

    dy = (
        face_point.y
        - wall.StartPoint.y
    )

    along = (
        dx * tangent.x
        + dy * tangent.y
    )

    wall_length = (
        wall.Length.Value
    )

    if width <= wall_length:
        along = max(
            half_width,
            min(
                wall_length
                - half_width,
                along,
            ),
        )

    back_centre = App.Vector(
        wall.StartPoint.x
        + tangent.x * along
        + normal.x * face_offset,
        wall.StartPoint.y
        + tangent.y * along
        + normal.y * face_offset,
        furniture.Position.z,
    )

    rotation = rotation_for_wall(
        wall,
        side,
    )

    angle = math.radians(
        rotation
    )

    local_x = App.Vector(
        math.cos(angle),
        math.sin(angle),
        0.0,
    )

    position = App.Vector(
        back_centre.x
        - local_x.x * half_width,
        back_centre.y
        - local_x.y * half_width,
        furniture.Position.z,
    )

    furniture.RotationAngle = (
        rotation
    )

    furniture.Position = (
        position
    )

    furniture.Document.recompute()


class FurnitureSnapWallTool:
    """Click a wall to snap furniture to it."""

    def __init__(
        self,
        furniture,
        on_finished=None,
    ):
        self.furniture = furniture
        self.document = (
            furniture.Document
        )

        self.on_finished = (
            on_finished
        )

        self.view = None
        self.callback = None
        self.escape_shortcut = None

        self.active = False

    def start(self):
        gui_document = (
            Gui.activeDocument()
        )

        if gui_document is None:
            return

        self.view = (
            gui_document.activeView()
        )

        self.active = True

        self.callback = (
            self.view.addEventCallback(
                "SoMouseButtonEvent",
                self._mouse_event,
            )
        )

        main_window = (
            Gui.getMainWindow()
        )

        self.escape_shortcut = (
            QtGui.QShortcut(
                QtGui.QKeySequence(
                    "Esc"
                ),
                main_window,
            )
        )

        self.escape_shortcut.setContext(
            QtCore.Qt.ShortcutContext.ApplicationShortcut
        )

        self.escape_shortcut.activated.connect(
            self.stop
        )

        try:
            main_window.statusBar().showMessage(
                "OpenInteriorCAD: click a wall. "
                "The cabinet will snap with its back "
                "edge against the wall. Esc = cancel."
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

        screen_position = (
            info.get(
                "Position"
            )
        )

        if screen_position is None:
            return

        object_info = (
            self.view.getObjectInfo(
                screen_position
            )
        )

        if not object_info:
            return

        object_name = (
            object_info.get(
                "Object"
            )
        )

        if not object_name:
            return

        wall = self.document.getObject(
            object_name
        )

        if wall is None:
            return

        if (
            getattr(
                wall,
                "OICType",
                "",
            )
            != WALL_TYPE
        ):
            return

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
            "Snap Furniture to Wall"
        )

        try:
            snap_to_wall(
                furniture=self.furniture,
                wall=wall,
                click_point=click_point,
            )

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD wall snap error: "
                f"{error}\n"
            )

            return

        self.stop()

        if self.on_finished is not None:
            try:
                self.on_finished()

            except Exception:
                pass

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
                self.escape_shortcut.setEnabled(
                    False
                )

                self.escape_shortcut.deleteLater()

            except Exception:
                pass

        self.escape_shortcut = None
        self.active = False

        try:
            Gui.getMainWindow().statusBar().clearMessage()

        except Exception:
            pass