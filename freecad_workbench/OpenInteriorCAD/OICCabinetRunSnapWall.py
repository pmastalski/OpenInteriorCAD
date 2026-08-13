"""Snap every cabinet in a Cabinet Run to the same selected wall face.

Behavior:
- click selects the wall and physical wall face only;
- each cabinet keeps its own position ALONG the wall;
- every cabinet rotates parallel to the wall;
- every cabinet back edge is placed at exactly the requested Wall Offset;
- no cabinet is moved toward a wall end or corner.
"""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui

from OICCabinetRun import (
    get_run_cabinets,
    update_run_properties,
)
from OICFurnitureSnapWall import (
    WALL_TYPE,
    get_selected_face,
    rotation_for_wall,
    wall_unit_vectors,
)


def local_axes(rotation):
    """Return cabinet local X (width) and Y (depth/front) axes."""

    angle = math.radians(rotation)

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

    return local_x, local_y


def cabinet_centre(cabinet):
    """Return the current footprint centre of a cabinet."""

    local_x, local_y = local_axes(
        cabinet.RotationAngle.Value
    )

    return App.Vector(
        cabinet.Position.x
        + local_x.x * cabinet.Width.Value / 2.0
        + local_y.x * cabinet.Depth.Value / 2.0,
        cabinet.Position.y
        + local_x.y * cabinet.Width.Value / 2.0
        + local_y.y * cabinet.Depth.Value / 2.0,
        cabinet.Position.z,
    )


def scalar_along(vector, axis):
    """Dot product helper."""

    return (
        vector.x * axis.x
        + vector.y * axis.y
    )


def snap_one_cabinet_to_wall_line(
    cabinet,
    wall,
    tangent,
    normal,
    target_rotation,
    target_back_distance,
):
    """
    Rotate one cabinet around its own centre and then translate it
    only perpendicular to the wall so its BACK edge lands exactly
    on the target wall-offset line.

    Its along-wall coordinate is preserved.
    """

    centre = cabinet_centre(
        cabinet
    )

    # Preserve the cabinet centre coordinate along the selected wall.
    centre_from_wall_start = App.Vector(
        centre.x - wall.StartPoint.x,
        centre.y - wall.StartPoint.y,
        0.0,
    )

    centre_along = scalar_along(
        centre_from_wall_start,
        tangent,
    )

    new_x, new_y = local_axes(
        target_rotation
    )

    # Back-centre -> cabinet centre is +Depth/2 along local Y.
    # Therefore the target cabinet centre is Depth/2 in front of
    # the target back line.
    #
    # local +Y points away from the wall because target_rotation
    # comes from rotation_for_wall().
    target_centre_normal = (
        target_back_distance
        + scalar_along(
            App.Vector(
                new_y.x * cabinet.Depth.Value / 2.0,
                new_y.y * cabinet.Depth.Value / 2.0,
                0.0,
            ),
            normal,
        )
    )

    # Rebuild the cabinet centre from:
    # 1) its unchanged coordinate ALONG the wall,
    # 2) the exact new coordinate NORMAL to the wall.
    target_centre = App.Vector(
        wall.StartPoint.x
        + tangent.x * centre_along
        + normal.x * target_centre_normal,
        wall.StartPoint.y
        + tangent.y * centre_along
        + normal.y * target_centre_normal,
        centre.z,
    )

    # Position is the local back-left corner.
    target_position = App.Vector(
        target_centre.x
        - new_x.x * cabinet.Width.Value / 2.0
        - new_y.x * cabinet.Depth.Value / 2.0,
        target_centre.y
        - new_x.y * cabinet.Width.Value / 2.0
        - new_y.y * cabinet.Depth.Value / 2.0,
        cabinet.Position.z,
    )

    cabinet.RotationAngle = (
        target_rotation
    )

    cabinet.Position = (
        target_position
    )


def snap_run_to_wall(
    run,
    wall,
    click_point,
    offset=0.0,
):
    """
    Snap ALL cabinets in a run independently to one wall-offset line.

    The click is used only to select the physical wall face.
    Every cabinet keeps its own along-wall position.
    """

    cabinets = get_run_cabinets(
        run
    )

    if not cabinets:
        raise ValueError(
            "Cabinet Run contains no cabinets."
        )

    tangent, normal = wall_unit_vectors(
        wall
    )

    (
        _distance,
        side,
        face_offset,
        _face_point,
        _segment_t,
    ) = get_selected_face(
        wall,
        click_point,
    )

    target_rotation = rotation_for_wall(
        wall,
        side,
    )

    # Selected physical wall face plus the requested offset.
    # side * offset means positive offset always moves away
    # from the wall body.
    target_back_distance = (
        face_offset
        + side * float(offset)
    )

    for cabinet in cabinets:
        snap_one_cabinet_to_wall_line(
            cabinet=cabinet,
            wall=wall,
            tangent=tangent,
            normal=normal,
            target_rotation=target_rotation,
            target_back_distance=target_back_distance,
        )

    update_run_properties(
        run
    )

    run.Document.recompute()


class CabinetRunSnapWallTool:
    """Interactive wall picker for a Cabinet Run."""

    def __init__(
        self,
        run,
        offset=0.0,
    ):
        self.run = run
        self.document = run.Document
        self.offset = float(
            offset
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
                "OpenInteriorCAD: click wall face. "
                "Every cabinet will keep its along-wall position "
                "and move independently perpendicular to the wall. "
                f"Offset = {self.offset:.1f} mm. Esc = cancel."
            )

        except Exception:
            pass

    def _mouse_event(
        self,
        info,
    ):
        if not self.active:
            return

        if info.get(
            "State"
        ) != "DOWN":
            return

        if info.get(
            "Button"
        ) != "BUTTON1":
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

        if getattr(
            wall,
            "OICType",
            "",
        ) != WALL_TYPE:
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
            "Snap Cabinet Run to Wall"
        )

        try:
            snap_run_to_wall(
                run=self.run,
                wall=wall,
                click_point=click_point,
                offset=self.offset,
            )

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD Cabinet Run wall snap error: "
                f"{error}\n"
            )

            return

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
