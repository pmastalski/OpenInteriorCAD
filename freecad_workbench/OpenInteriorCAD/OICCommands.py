"""GUI commands for the OpenInteriorCAD FreeCAD workbench."""

import FreeCAD as App
import FreeCADGui as Gui
from OICIcons import icon
from OICDoorEditPanel import DoorEditPanel
from PySide import QtCore, QtGui, QtWidgets
from OICDoorPanel import DoorPanel
from OICEditWallPanel import EditWallPanel
from OICRoom import (
    add_wall_to_room,
    close_room,
    create_room,
)
from OICWall import (
    create_wall,
    normalize_angle,
)
from OICWallPanel import WallDrawingPanel


ACTIVE_DRAW_TOOL = None


class NumericalRoomDrawingTool:
    """Numerical room drawing using length and relative angle."""

    def __init__(self):
        self.document = None
        self.view = None
        self.panel = None

        self.room = None

        self.first_point = None
        self.current_point = None
        self.current_heading = None

        self.mouse_callback = None
        self.escape_shortcut = None

        self.wall_history = []

        self.active = False

    def start(self):
        """Start numerical room drawing."""

        global ACTIVE_DRAW_TOOL

        self.document = App.ActiveDocument

        if self.document is None:
            self.document = App.newDocument(
                "OpenInteriorCAD"
            )

        gui_document = Gui.activeDocument()

        if gui_document is None:
            App.Console.PrintError(
                "OpenInteriorCAD: brak aktywnego widoku.\n"
            )
            return

        self.view = gui_document.activeView()

        self.view.viewTop()

        self.active = True

        ACTIVE_DRAW_TOOL = self

        self._create_escape_shortcut()

        self.panel = WallDrawingPanel(
            self
        )

        self.request_start_point()

        Gui.Control.showDialog(
            self.panel
        )

    def _create_escape_shortcut(self):
        """Create application-wide Escape shortcut."""

        main_window = Gui.getMainWindow()

        self.escape_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence(
                "Esc"
            ),
            main_window,
        )

        self.escape_shortcut.setContext(
            QtCore.Qt.ShortcutContext.ApplicationShortcut
        )

        self.escape_shortcut.activated.connect(
            self._escape_pressed
        )

    def _remove_escape_shortcut(self):
        if self.escape_shortcut is None:
            return

        self.escape_shortcut.setEnabled(
            False
        )

        self.escape_shortcut.deleteLater()

        self.escape_shortcut = None

    def _escape_pressed(self):
        self.stop(
            close_panel=True
        )

    def request_start_point(self):
        """Wait for first room point."""

        if not self.active:
            return

        self._remove_mouse_callback()

        self.room = None
        self.first_point = None
        self.current_point = None
        self.current_heading = None

        self.wall_history = []

        self.mouse_callback = (
            self.view.addEventCallback(
                "SoMouseButtonEvent",
                self._handle_start_click,
            )
        )

        if self.panel is not None:
            self.panel.set_waiting_for_start()

    def _handle_start_click(
        self,
        info,
    ):
        """Store first room point."""

        if not self.active:
            return

        if info.get("State") != "DOWN":
            return

        if info.get("Button") != "BUTTON1":
            return

        position = info.get(
            "Position"
        )

        if position is None:
            return

        try:
            point = self.view.getPoint(
                position[0],
                position[1],
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD: błąd getPoint: "
                f"{error}\n"
            )

            return

        start_point = App.Vector(
            point.x,
            point.y,
            0.0,
        )

        self._remove_mouse_callback()

        self.document.openTransaction(
            "Nowe pomieszczenie"
        )

        try:
            self.room = create_room(
                self.document
            )

            self.document.recompute()

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD: błąd tworzenia "
                f"pomieszczenia: {error}\n"
            )

            return

        self.first_point = start_point
        self.current_point = start_point
        self.current_heading = None

        self.wall_history = []

        self.panel.set_start_point_ready()

    def add_wall(
        self,
        length,
        relative_angle,
        thickness,
        height,
    ):
        """Add one parametric wall."""

        if not self.active:
            return

        if self.room is None:
            return

        if self.current_point is None:
            return

        wall = create_wall(
            document=self.document,
            start_point=self.current_point,
            length=length,
            angle=relative_angle,
        )

        wall.Thickness = thickness
        wall.Height = height

        add_wall_to_room(
            self.room,
            wall,
        )

        self.document.recompute()

        wall.ViewObject.Visibility = True

        self.current_point = App.Vector(
            wall.EndPoint.x,
            wall.EndPoint.y,
            wall.EndPoint.z,
        )

        self.current_heading = (
            wall.Heading.Value
        )

        self.wall_history.append(
            wall
        )

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            wall
        )

        self.panel.set_wall_added(
            wall_count=self.room.WallCount,
            heading=self.current_heading,
        )

        try:
            self.view.fitAll()

        except Exception:
            pass

    def undo_last_wall(self):
        """Remove last wall."""

        if self.room is None:
            return

        if not self.wall_history:
            return

        wall = self.wall_history.pop()

        self.document.openTransaction(
            "Cofnij ostatnią ścianę"
        )

        try:
            if wall in self.room.Group:
                self.room.removeObject(
                    wall
                )

            self.document.removeObject(
                wall.Name
            )

            self.room.WallCount = len(
                self.wall_history
            )

            self.document.recompute()

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD: błąd cofania "
                f"ściany: {error}\n"
            )

            return

        if self.wall_history:
            previous = self.wall_history[-1]

            self.current_point = App.Vector(
                previous.EndPoint.x,
                previous.EndPoint.y,
                previous.EndPoint.z,
            )

            self.current_heading = (
                previous.Heading.Value
            )

        else:
            self.current_point = App.Vector(
                self.first_point.x,
                self.first_point.y,
                self.first_point.z,
            )

            self.current_heading = None

        self.panel.set_after_undo(
            wall_count=len(
                self.wall_history
            ),
            heading=self.current_heading,
        )

    def close_current_room(
        self,
        thickness,
        height,
    ):
        """Close room."""

        if self.room is None:
            return

        if self.first_point is None:
            return

        if self.current_point is None:
            return

        if self.room.WallCount < 2:
            return

        previous_heading = (
            self.current_heading
            if self.current_heading is not None
            else 0.0
        )

        dx = (
            self.first_point.x
            - self.current_point.x
        )

        dy = (
            self.first_point.y
            - self.current_point.y
        )

        closing_length = (
            dx * dx
            + dy * dy
        ) ** 0.5

        if closing_length > 1.0:
            absolute_heading = App.Vector(
                dx,
                dy,
                0.0,
            ).getAngle(
                App.Vector(
                    1.0,
                    0.0,
                    0.0,
                )
            )

            absolute_heading = (
                absolute_heading
                * 180.0
                / 3.141592653589793
            )

            if dy < 0:
                absolute_heading = (
                    -absolute_heading
                )

            relative_angle = normalize_angle(
                absolute_heading
                - previous_heading
            )

            closing_wall = create_wall(
                document=self.document,
                start_point=self.current_point,
                length=closing_length,
                angle=relative_angle,
            )

            closing_wall.Thickness = thickness
            closing_wall.Height = height
            closing_wall.AutoClose = True

            add_wall_to_room(
                self.room,
                closing_wall,
            )

        close_room(
            self.room
        )

        self.document.recompute()

        self.room = None
        self.first_point = None
        self.current_point = None
        self.current_heading = None

        self.wall_history = []

        self.panel.set_room_closed()

        self.mouse_callback = (
            self.view.addEventCallback(
                "SoMouseButtonEvent",
                self._handle_start_click,
            )
        )

    def _remove_mouse_callback(self):
        if (
            self.view is not None
            and self.mouse_callback is not None
        ):
            try:
                self.view.removeEventCallback(
                    "SoMouseButtonEvent",
                    self.mouse_callback,
                )

            except Exception:
                pass

        self.mouse_callback = None

    def stop(
        self,
        close_panel=False,
    ):
        """Completely stop the drawing tool."""

        global ACTIVE_DRAW_TOOL

        if not self.active:
            if close_panel and Gui.Control.activeDialog():
                Gui.Control.closeDialog()

            return

        self._remove_mouse_callback()
        self._remove_escape_shortcut()

        self.room = None
        self.first_point = None
        self.current_point = None
        self.current_heading = None

        self.wall_history = []

        self.active = False

        ACTIVE_DRAW_TOOL = None

        if close_panel and Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        App.Console.PrintMessage(
            "OpenInteriorCAD: zakończono "
            "rysowanie pomieszczenia.\n"
        )


class DrawRoomCommand:
    """Numerical room drawing."""

    def GetResources(self):
        return {
            "Pixmap": icon("draw_room.svg"),
            "MenuText": "Draw Room",
            "ToolTip": "Draw a room using length and relative angle.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_DRAW_TOOL

        # Drugie kliknięcie tego samego przycisku
        # kończy aktywne narzędzie.
        if (
            ACTIVE_DRAW_TOOL is not None
            and ACTIVE_DRAW_TOOL.active
        ):
            ACTIVE_DRAW_TOOL.stop(
                close_panel=True
            )

            return

        if Gui.Control.activeDialog():
            QtWidgets.QMessageBox.information(
                Gui.getMainWindow(),
                "OpenInteriorCAD",
                "Zamknij najpierw aktywny panel.",
            )

            return

        tool = NumericalRoomDrawingTool()

        tool.start()


class EditWallCommand:
    """Edit selected wall."""

    def GetResources(self):
        return {
            "Pixmap": icon("edit_wall.svg"),
            "MenuText": "Edit Wall",
            "ToolTip": "Edit the selected wall.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_DRAW_TOOL

        # Jeśli rysowanie nadal trwa, kończymy je
        # automatycznie przed edycją.
        if (
            ACTIVE_DRAW_TOOL is not None
            and ACTIVE_DRAW_TOOL.active
        ):
            ACTIVE_DRAW_TOOL.stop(
                close_panel=True
            )

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Edytuj ścianę",
                "Zaznacz dokładnie jedną ścianę.",
            )

            return

        wall = selection[0]

        if (
            getattr(
                wall,
                "OICType",
                "",
            )
            != "OpenInteriorCAD::Wall"
        ):
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Edytuj ścianę",
                "Zaznaczony obiekt nie jest ścianą.",
            )

            return

        panel = EditWallPanel(
            wall
        )

        Gui.Control.showDialog(
            panel
        )

class AddDoorCommand:
    """Insert a door into the selected wall."""

    def GetResources(self):
        return {
            "Pixmap": icon("add_door.svg"),
            "MenuText": "Add Door",
            "ToolTip": "Add a door to the selected wall.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_DRAW_TOOL

        if (
            ACTIVE_DRAW_TOOL is not None
            and ACTIVE_DRAW_TOOL.active
        ):
            ACTIVE_DRAW_TOOL.stop(
                close_panel=True
            )

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Dodaj drzwi",
                "Zaznacz dokładnie jedną ścianę.",
            )
            return

        wall = selection[0]

        if (
            getattr(
                wall,
                "OICType",
                "",
            )
            != "OpenInteriorCAD::Wall"
        ):
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Dodaj drzwi",
                "Zaznaczony obiekt nie jest ścianą.",
            )
            return

        panel = DoorPanel(
            wall
        )

        Gui.Control.showDialog(
            panel
        )

class EditDoorCommand:
    """Edit selected OpenInteriorCAD door."""

    def GetResources(self):
        return {
            "Pixmap": icon("edit_door.svg"),
            "MenuText": "Edit Door",
            "ToolTip": "Edit door size, position and opening direction.",
        }

    def IsActive(self):
        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            return False

        return (
            getattr(
                selection[0],
                "OICType",
                "",
            )
            == "OpenInteriorCAD::Door"
        )

    def Activated(self):
        global ACTIVE_DRAW_TOOL

        if (
            ACTIVE_DRAW_TOOL is not None
            and ACTIVE_DRAW_TOOL.active
        ):
            ACTIVE_DRAW_TOOL.stop(
                close_panel=True
            )

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            return

        door = selection[0]

        if (
            getattr(
                door,
                "OICType",
                "",
            )
            != "OpenInteriorCAD::Door"
        ):
            return

        panel = DoorEditPanel(
            door
        )

        Gui.Control.showDialog(
            panel
        )

Gui.addCommand(
    "OIC_DrawRoomV2",
    DrawRoomCommand(),
)

Gui.addCommand(
    "OIC_EditWallV2",
    EditWallCommand(),
)

Gui.addCommand(
    "OIC_AddDoor",
    AddDoorCommand(),
)

Gui.addCommand(
    "OIC_EditDoor",
    EditDoorCommand(),
)