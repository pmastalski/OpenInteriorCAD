"""Set exact perpendicular furniture clearance from a wall."""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui


WALL_TYPE = "OpenInteriorCAD::Wall"

REFERENCE_AXIS = "Oś"
REFERENCE_LEFT = "Lewa krawędź"
REFERENCE_RIGHT = "Prawa krawędź"


# ============================================================
# WALL GEOMETRY
# ============================================================

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
    """
    Return signed offsets of both physical wall faces
    from the logical wall reference line.
    """

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


# ============================================================
# FURNITURE FOOTPRINT
# ============================================================

def furniture_axes(furniture):
    """Return furniture local X and Y axes."""

    angle = math.radians(
        furniture.RotationAngle.Value
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


def furniture_corners(furniture):
    """
    Return actual four footprint corners of
    rotated furniture.

    Position = local back-left corner.
    """

    local_x, local_y = (
        furniture_axes(
            furniture
        )
    )

    position = (
        furniture.Position
    )

    width = (
        furniture.Width.Value
    )

    depth = (
        furniture.Depth.Value
    )

    p0 = App.Vector(
        position.x,
        position.y,
        position.z,
    )

    p1 = App.Vector(
        position.x
        + local_x.x * width,
        position.y
        + local_x.y * width,
        position.z,
    )

    p2 = App.Vector(
        position.x
        + local_y.x * depth,
        position.y
        + local_y.y * depth,
        position.z,
    )

    p3 = App.Vector(
        position.x
        + local_x.x * width
        + local_y.x * depth,
        position.y
        + local_x.y * width
        + local_y.y * depth,
        position.z,
    )

    return [
        p0,
        p1,
        p2,
        p3,
    ]


# ============================================================
# PROJECTIONS
# ============================================================

def signed_normal_coordinate(
    point,
    wall,
    normal,
):
    """
    Signed perpendicular coordinate of a point
    relative to wall logical axis.
    """

    dx = (
        point.x
        - wall.StartPoint.x
    )

    dy = (
        point.y
        - wall.StartPoint.y
    )

    return (
        dx * normal.x
        + dy * normal.y
    )


def furniture_normal_range(
    furniture,
    wall,
    normal,
):
    """
    Return minimum and maximum perpendicular
    coordinates occupied by actual furniture footprint.
    """

    values = []

    for point in furniture_corners(
        furniture
    ):
        values.append(
            signed_normal_coordinate(
                point,
                wall,
                normal,
            )
        )

    return (
        min(values),
        max(values),
    )


def furniture_centre_normal_coordinate(
    furniture,
    wall,
    normal,
):
    """Return furniture footprint centre coordinate."""

    minimum, maximum = (
        furniture_normal_range(
            furniture,
            wall,
            normal,
        )
    )

    return (
        minimum + maximum
    ) / 2.0


# ============================================================
# WALL OFFSET
# ============================================================

def set_wall_offset(
    furniture,
    wall,
    offset,
):
    """
    Move furniture ONLY perpendicular to selected wall.

    No rotation.
    No movement along wall.

    The ACTUAL nearest furniture edge is placed
    exactly `offset` mm from the physical wall face.
    """

    _, normal = (
        wall_unit_vectors(
            wall
        )
    )

    positive_face, negative_face = (
        wall_face_offsets(
            wall
        )
    )

    furniture_min, furniture_max = (
        furniture_normal_range(
            furniture,
            wall,
            normal,
        )
    )

    furniture_centre = (
        furniture_min
        + furniture_max
    ) / 2.0

    # --------------------------------------------------------
    # DETERMINE WHICH SIDE OF WALL THE CABINET IS ON
    # --------------------------------------------------------

    wall_middle = (
        positive_face
        + negative_face
    ) / 2.0

    if furniture_centre >= wall_middle:
        side = 1.0

    else:
        side = -1.0

    # --------------------------------------------------------
    # POSITIVE SIDE
    #
    # Wall face is positive_face.
    # Closest furniture edge is furniture_min.
    #
    # Desired:
    #
    # furniture_min = positive_face + offset
    # --------------------------------------------------------

    if side > 0.0:
        current_edge = (
            furniture_min
        )

        target_edge = (
            positive_face
            + offset
        )

    # --------------------------------------------------------
    # NEGATIVE SIDE
    #
    # Wall face is negative_face.
    # Closest furniture edge is furniture_max.
    #
    # Desired:
    #
    # furniture_max = negative_face - offset
    # --------------------------------------------------------

    else:
        current_edge = (
            furniture_max
        )

        target_edge = (
            negative_face
            - offset
        )

    movement_distance = (
        target_edge
        - current_edge
    )

    # --------------------------------------------------------
    # PURE NORMAL TRANSLATION
    # --------------------------------------------------------

    movement = App.Vector(
        normal.x
        * movement_distance,
        normal.y
        * movement_distance,
        0.0,
    )

    furniture.Position = App.Vector(
        furniture.Position.x
        + movement.x,
        furniture.Position.y
        + movement.y,
        furniture.Position.z,
    )

    furniture.Document.recompute()

    # Diagnostic information.
    App.Console.PrintMessage(
        "OpenInteriorCAD Wall Offset:\n"
        f"  wall = {wall.Label}\n"
        f"  offset = {offset:.3f} mm\n"
        f"  side = {side:+.0f}\n"
        f"  furniture range before = "
        f"{furniture_min:.3f} .. "
        f"{furniture_max:.3f}\n"
        f"  wall faces = "
        f"{negative_face:.3f} .. "
        f"{positive_face:.3f}\n"
        f"  translation = "
        f"{movement_distance:.3f} mm\n"
    )


# ============================================================
# INTERACTIVE TOOL
# ============================================================

class FurnitureWallOffsetTool:
    """Select wall and set exact furniture clearance."""

    def __init__(
        self,
        furniture,
        offset=0.0,
        on_finished=None,
    ):
        self.furniture = furniture

        self.document = (
            furniture.Document
        )

        self.offset = (
            offset
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
                "OpenInteriorCAD: select reference wall. "
                f"Clearance = {self.offset:.1f} mm. "
                "Furniture will move perpendicular only."
            )

        except Exception:
            pass

    def _mouse_event(
        self,
        info,
    ):
        if not self.active:
            return

        if (
            info.get("State")
            != "DOWN"
        ):
            return

        if (
            info.get("Button")
            != "BUTTON1"
        ):
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

        self.document.openTransaction(
            "Set Furniture Wall Clearance"
        )

        try:
            set_wall_offset(
                furniture=self.furniture,
                wall=wall,
                offset=self.offset,
            )

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD Wall Offset error: "
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