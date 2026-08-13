"""Diagnostic furniture movement and wall snapping for OpenInteriorCAD."""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui


WALL_TYPE = "OpenInteriorCAD::Wall"

REFERENCE_AXIS = "Oś"
REFERENCE_LEFT = "Lewa krawędź"
REFERENCE_RIGHT = "Prawa krawędź"

SNAP_DISTANCE = 450.0


# ============================================================
# DEBUG
# ============================================================

def debug(text=""):
    App.Console.PrintMessage(
        str(text) + "\n"
    )


def debug_vector(
    name,
    vector,
):
    debug(
        f"{name}: "
        f"X={vector.x:.3f}, "
        f"Y={vector.y:.3f}, "
        f"Z={vector.z:.3f}"
    )


def separator():
    debug(
        "=" * 70
    )


# ============================================================
# BASIC GEOMETRY
# ============================================================

def normalize_angle(angle):
    return (
        angle + 180.0
    ) % 360.0 - 180.0


def get_all_walls(document):
    if document is None:
        return []

    return [
        obj
        for obj in document.Objects
        if getattr(
            obj,
            "OICType",
            "",
        )
        == WALL_TYPE
    ]


def wall_unit_vectors(wall):
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


def point_to_segment(
    point,
    start,
    end,
):
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


# ============================================================
# WALL FACES
# ============================================================

def wall_face_offsets(wall):
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


def make_wall_face_segment(
    wall,
    offset,
):
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


# ============================================================
# DIAGNOSTICS
# ============================================================

def print_wall_diagnostics(
    wall,
    click_point,
):
    separator()

    debug(
        f"ŚCIANA: {wall.Name} / {wall.Label}"
    )

    debug(
        f"OICType: "
        f"{getattr(wall, 'OICType', 'BRAK')}"
    )

    debug(
        f"ReferenceLine: "
        f"{getattr(wall, 'ReferenceLine', 'BRAK')}"
    )

    try:
        debug(
            f"Thickness: "
            f"{wall.Thickness.Value:.3f} mm"
        )
    except Exception:
        debug(
            "Thickness: BŁĄD"
        )

    try:
        debug(
            f"Length: "
            f"{wall.Length.Value:.3f} mm"
        )
    except Exception:
        debug(
            "Length: BŁĄD"
        )

    try:
        debug(
            f"Heading: "
            f"{wall.Heading.Value:.3f} deg"
        )
    except Exception:
        debug(
            "Heading: BŁĄD"
        )

    debug_vector(
        "StartPoint",
        wall.StartPoint,
    )

    debug_vector(
        "EndPoint",
        wall.EndPoint,
    )

    tangent, normal = (
        wall_unit_vectors(
            wall
        )
    )

    debug_vector(
        "Tangent",
        tangent,
    )

    debug_vector(
        "Normal",
        normal,
    )

    positive_offset, negative_offset = (
        wall_face_offsets(
            wall
        )
    )

    debug(
        f"Positive face offset: "
        f"{positive_offset:.3f}"
    )

    debug(
        f"Negative face offset: "
        f"{negative_offset:.3f}"
    )

    positive_start, positive_end = (
        make_wall_face_segment(
            wall,
            positive_offset,
        )
    )

    negative_start, negative_end = (
        make_wall_face_segment(
            wall,
            negative_offset,
        )
    )

    debug_vector(
        "POS face START",
        positive_start,
    )

    debug_vector(
        "POS face END",
        positive_end,
    )

    debug_vector(
        "NEG face START",
        negative_start,
    )

    debug_vector(
        "NEG face END",
        negative_end,
    )

    (
        pos_closest,
        pos_distance,
        pos_t,
    ) = point_to_segment(
        click_point,
        positive_start,
        positive_end,
    )

    (
        neg_closest,
        neg_distance,
        neg_t,
    ) = point_to_segment(
        click_point,
        negative_start,
        negative_end,
    )

    debug_vector(
        "POS closest",
        pos_closest,
    )

    debug(
        f"POS distance: "
        f"{pos_distance:.3f} mm"
    )

    debug(
        f"POS t: "
        f"{pos_t:.6f}"
    )

    debug_vector(
        "NEG closest",
        neg_closest,
    )

    debug(
        f"NEG distance: "
        f"{neg_distance:.3f} mm"
    )

    debug(
        f"NEG t: "
        f"{neg_t:.6f}"
    )


def print_furniture_before(
    furniture,
):
    separator()

    debug(
        "SZAFKA PRZED PRZESUNIĘCIEM"
    )

    debug(
        f"Name: {furniture.Name}"
    )

    debug(
        f"Label: {furniture.Label}"
    )

    debug(
        f"Width: "
        f"{furniture.Width.Value:.3f}"
    )

    debug(
        f"Depth: "
        f"{furniture.Depth.Value:.3f}"
    )

    debug(
        f"Height: "
        f"{furniture.Height.Value:.3f}"
    )

    debug(
        f"RotationAngle: "
        f"{furniture.RotationAngle.Value:.3f}"
    )

    debug_vector(
        "Position",
        furniture.Position,
    )

    try:
        debug_vector(
            "Shape BB Min",
            App.Vector(
                furniture.Shape.BoundBox.XMin,
                furniture.Shape.BoundBox.YMin,
                furniture.Shape.BoundBox.ZMin,
            ),
        )

        debug_vector(
            "Shape BB Max",
            App.Vector(
                furniture.Shape.BoundBox.XMax,
                furniture.Shape.BoundBox.YMax,
                furniture.Shape.BoundBox.ZMax,
            ),
        )

    except Exception as error:
        debug(
            f"BoundBox ERROR: {error}"
        )


# ============================================================
# FIND NEAREST FACE
# ============================================================

def find_nearest_wall_face(
    document,
    click_point,
):
    best_wall = None
    best_point = None
    best_distance = None
    best_side = None
    best_t = None
    best_offset = None

    debug("")
    debug(
        "ANALIZA WSZYSTKICH ŚCIAN"
    )

    for wall in get_all_walls(
        document
    ):
        print_wall_diagnostics(
            wall,
            click_point,
        )

        positive_offset, negative_offset = (
            wall_face_offsets(
                wall
            )
        )

        faces = [
            (
                1.0,
                positive_offset,
                "POSITIVE",
            ),
            (
                -1.0,
                negative_offset,
                "NEGATIVE",
            ),
        ]

        for side, offset, face_name in faces:
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

            if (
                best_distance is None
                or distance < best_distance
            ):
                best_wall = wall
                best_point = closest
                best_distance = distance
                best_side = side
                best_t = t
                best_offset = offset

                debug(
                    ">>> NOWY NAJBLIŻSZY:"
                )

                debug(
                    f"    wall={wall.Label}"
                )

                debug(
                    f"    face={face_name}"
                )

                debug(
                    f"    distance="
                    f"{distance:.3f}"
                )

    return (
        best_wall,
        best_point,
        best_distance,
        best_side,
        best_t,
        best_offset,
    )


# ============================================================
# ROTATION
# ============================================================

def rotation_for_wall_face(
    wall,
    side,
):
    _, normal = wall_unit_vectors(
        wall
    )

    front_x = (
        normal.x * side
    )

    front_y = (
        normal.y * side
    )

    angle = math.degrees(
        math.atan2(
            -front_x,
            front_y,
        )
    )

    angle = normalize_angle(
        angle
    )

    debug("")
    debug(
        "OBLICZENIE OBROTU"
    )

    debug_vector(
        "Wall normal",
        normal,
    )

    debug(
        f"Side: {side:+.0f}"
    )

    debug(
        f"Desired furniture +Y: "
        f"X={front_x:.3f}, "
        f"Y={front_y:.3f}"
    )

    debug(
        f"Calculated rotation: "
        f"{angle:.3f} deg"
    )

    return angle


# ============================================================
# SNAP
# ============================================================

def snap_furniture_to_wall(
    furniture,
    wall,
    face_point,
    side,
    face_offset,
):
    separator()

    debug(
        "ROZPOCZYNAM SNAP"
    )

    tangent, normal = (
        wall_unit_vectors(
            wall
        )
    )

    width = (
        furniture.Width.Value
    )

    depth = (
        furniture.Depth.Value
    )

    debug(
        f"Furniture width: "
        f"{width:.3f}"
    )

    debug(
        f"Furniture depth: "
        f"{depth:.3f}"
    )

    debug_vector(
        "Selected face point",
        face_point,
    )

    debug(
        f"Selected face offset: "
        f"{face_offset:.3f}"
    )

    rotation = (
        rotation_for_wall_face(
            wall,
            side,
        )
    )

    # ------------------------------------------------
    # Determine position along wall
    # ------------------------------------------------

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

    debug(
        f"Along wall BEFORE clamp: "
        f"{along:.3f}"
    )

    wall_length = (
        wall.Length.Value
    )

    half_width = (
        width / 2.0
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

    debug(
        f"Along wall AFTER clamp: "
        f"{along:.3f}"
    )

    # ------------------------------------------------
    # Exact centre of back edge on chosen wall face
    # ------------------------------------------------

    back_centre = App.Vector(
        wall.StartPoint.x
        + tangent.x * along
        + normal.x * face_offset,
        wall.StartPoint.y
        + tangent.y * along
        + normal.y * face_offset,
        furniture.Position.z,
    )

    debug_vector(
        "Back centre TARGET",
        back_centre,
    )

    # ------------------------------------------------
    # Local furniture axes after rotation
    # ------------------------------------------------

    angle_rad = math.radians(
        rotation
    )

    local_x = App.Vector(
        math.cos(
            angle_rad
        ),
        math.sin(
            angle_rad
        ),
        0.0,
    )

    local_y = App.Vector(
        -math.sin(
            angle_rad
        ),
        math.cos(
            angle_rad
        ),
        0.0,
    )

    debug_vector(
        "Furniture local +X",
        local_x,
    )

    debug_vector(
        "Furniture local +Y",
        local_y,
    )

    # ------------------------------------------------
    # Calculate origin
    # ------------------------------------------------

    position = App.Vector(
        back_centre.x
        - local_x.x
        * half_width,
        back_centre.y
        - local_x.y
        * half_width,
        furniture.Position.z,
    )

    debug_vector(
        "Calculated Position",
        position,
    )

    debug(
        f"Calculated Rotation: "
        f"{rotation:.3f}"
    )

    # ------------------------------------------------
    # Apply
    # ------------------------------------------------

    furniture.RotationAngle = (
        rotation
    )

    furniture.Position = (
        position
    )

    furniture.Document.recompute()

    # ------------------------------------------------
    # Diagnostics AFTER recompute
    # ------------------------------------------------

    separator()

    debug(
        "SZAFKA PO RECOMPUTE"
    )

    debug_vector(
        "Actual Position",
        furniture.Position,
    )

    debug(
        f"Actual RotationAngle: "
        f"{furniture.RotationAngle.Value:.3f}"
    )

    try:
        box = (
            furniture.Shape.BoundBox
        )

        debug(
            f"BOUNDING BOX:"
        )

        debug(
            f"XMin={box.XMin:.3f}"
        )

        debug(
            f"XMax={box.XMax:.3f}"
        )

        debug(
            f"YMin={box.YMin:.3f}"
        )

        debug(
            f"YMax={box.YMax:.3f}"
        )

        debug(
            f"ZMin={box.ZMin:.3f}"
        )

        debug(
            f"ZMax={box.ZMax:.3f}"
        )

    except Exception as error:
        debug(
            f"BoundBox ERROR: {error}"
        )

    separator()


# ============================================================
# MOVE TOOL
# ============================================================

class FurnitureMoveTool:
    """Diagnostic interactive furniture movement."""

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
            self.cancel
        )

        try:
            main_window.statusBar().showMessage(
                "TRYB DIAGNOSTYCZNY: "
                "kliknij przy ścianie. "
                "Dane pojawią się w Python Console."
            )

        except Exception:
            pass

        separator()

        debug(
            "START: PRZESUŃ MEBEL"
        )

        print_furniture_before(
            self.furniture
        )

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

        mouse_position = (
            info.get(
                "Position"
            )
        )

        if mouse_position is None:
            return

        try:
            point = (
                self.view.getPoint(
                    mouse_position[0],
                    mouse_position[1],
                )
            )

        except Exception as error:
            debug(
                f"GET POINT ERROR: {error}"
            )
            return

        click_point = App.Vector(
            point.x,
            point.y,
            0.0,
        )

        separator()

        debug(
            "KLIKNIĘCIE"
        )

        debug(
            f"Screen X: "
            f"{mouse_position[0]}"
        )

        debug(
            f"Screen Y: "
            f"{mouse_position[1]}"
        )

        debug_vector(
            "World click",
            click_point,
        )

        (
            wall,
            face_point,
            distance,
            side,
            t,
            face_offset,
        ) = find_nearest_wall_face(
            self.document,
            click_point,
        )

        separator()

        debug(
            "WYNIK WYBORU ŚCIANY"
        )

        if wall is None:
            debug(
                "NIE ZNALEZIONO ŚCIANY"
            )

        else:
            debug(
                f"Wall Name: "
                f"{wall.Name}"
            )

            debug(
                f"Wall Label: "
                f"{wall.Label}"
            )

            debug(
                f"Heading: "
                f"{wall.Heading.Value:.3f}"
            )

            debug(
                f"ReferenceLine: "
                f"{wall.ReferenceLine}"
            )

            debug(
                f"Thickness: "
                f"{wall.Thickness.Value:.3f}"
            )

            debug(
                f"Selected side: "
                f"{side:+.0f}"
            )

            debug(
                f"Selected face offset: "
                f"{face_offset:.3f}"
            )

            debug(
                f"Distance to selected face: "
                f"{distance:.3f}"
            )

            debug(
                f"Segment t: "
                f"{t:.6f}"
            )

            debug_vector(
                "Closest face point",
                face_point,
            )

        if (
            wall is None
            or distance is None
            or distance > SNAP_DISTANCE
        ):
            separator()

            debug(
                "BRAK SNAPOWANIA"
            )

            if distance is not None:
                debug(
                    f"Distance = "
                    f"{distance:.3f}"
                )

            debug(
                f"SNAP_DISTANCE = "
                f"{SNAP_DISTANCE:.3f}"
            )

            self.stop()

            return

        self.document.openTransaction(
            "Diagnostic furniture snap"
        )

        try:
            snap_furniture_to_wall(
                furniture=self.furniture,
                wall=wall,
                face_point=face_point,
                side=side,
                face_offset=face_offset,
            )

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            separator()

            debug(
                "SNAP ERROR"
            )

            debug(
                repr(error)
            )

            self.stop()

            return

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            self.furniture
        )

        self.stop()

        try:
            self.view.redraw()

        except Exception:
            pass

    def cancel(self):
        if not self.active:
            return

        debug(
            "DIAGNOSTYKA ANULOWANA"
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