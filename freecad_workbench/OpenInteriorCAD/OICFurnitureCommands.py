"""Furniture commands for OpenInteriorCAD."""

import FreeCAD as App
import FreeCADGui as Gui
from OICIcons import icon
from OICFurnitureDuplicatePanel import (
    FurnitureDuplicatePanel,
)
from PySide import QtWidgets

from OICFurniture import create_furniture
from OICFurnitureEditPanel import FurnitureEditPanel

from OICFurnitureMovePanel import (
    FurnitureMovePanel,
)

from OICFurniturePanel import FurniturePanel
from OICFurnitureSnapFurniture import (
    FurnitureSnapFurnitureTool,
)
from OICFurnitureSnapWall import (
    FurnitureSnapWallTool,
)


ACTIVE_FURNITURE_TOOL = None
ACTIVE_MOVE_TOOL = None
ACTIVE_SNAP_TOOL = None


def get_selected_furniture(title):
    """Return one selected furniture object."""

    selection = Gui.Selection.getSelection()

    if len(selection) != 1:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(),
            title,
            "Zaznacz dokładnie jeden mebel.",
        )
        return None

    furniture = selection[0]

    if (
        getattr(
            furniture,
            "OICType",
            "",
        )
        != "OpenInteriorCAD::Furniture"
    ):
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(),
            title,
            "Zaznaczony obiekt nie jest meblem.",
        )
        return None

    return furniture


def stop_active_tools():
    """Stop all active furniture tools."""

    global ACTIVE_FURNITURE_TOOL
    global ACTIVE_MOVE_TOOL
    global ACTIVE_SNAP_TOOL

    if (
        ACTIVE_FURNITURE_TOOL is not None
        and ACTIVE_FURNITURE_TOOL.active
    ):
        ACTIVE_FURNITURE_TOOL.stop(
            close_panel=True
        )

    ACTIVE_FURNITURE_TOOL = None

    if (
        ACTIVE_MOVE_TOOL is not None
        and ACTIVE_MOVE_TOOL.active
    ):
        ACTIVE_MOVE_TOOL.stop()

    ACTIVE_MOVE_TOOL = None

    if (
        ACTIVE_SNAP_TOOL is not None
        and ACTIVE_SNAP_TOOL.active
    ):
        ACTIVE_SNAP_TOOL.stop()

    ACTIVE_SNAP_TOOL = None


class FurniturePlacementTool:
    """Interactive cabinet placement tool."""

    def __init__(self):
        self.document = None
        self.view = None
        self.panel = None

        self.callback = None

        self.width = 600.0
        self.depth = 600.0
        self.height = 850.0
        self.rotation = 0.0

        self.active = False
        self.waiting_for_point = False

    def start(self):
        global ACTIVE_FURNITURE_TOOL

        self.document = App.ActiveDocument

        if self.document is None:
            self.document = App.newDocument(
                "OpenInteriorCAD"
            )

        gui_document = Gui.activeDocument()

        if gui_document is None:
            return

        self.view = gui_document.activeView()

        self.active = True
        ACTIVE_FURNITURE_TOOL = self

        self.panel = FurniturePanel(
            self
        )

        Gui.Control.showDialog(
            self.panel
        )

    def start_placement(
        self,
        width,
        depth,
        height,
        rotation,
    ):
        if not self.active:
            return

        self.width = width
        self.depth = depth
        self.height = height
        self.rotation = rotation

        self._remove_callback()

        self.waiting_for_point = True

        self.callback = (
            self.view.addEventCallback(
                "SoMouseButtonEvent",
                self._mouse_event,
            )
        )

    def _mouse_event(
        self,
        info,
    ):
        if not self.active:
            return

        if not self.waiting_for_point:
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
                "OpenInteriorCAD furniture point error: "
                f"{error}\n"
            )
            return

        self.waiting_for_point = False

        self._remove_callback()

        furniture_position = App.Vector(
            point.x,
            point.y,
            0.0,
        )

        self.document.openTransaction(
            "Wstaw szafkę"
        )

        try:
            furniture = create_furniture(
                document=self.document,
                position=furniture_position,
                width=self.width,
                depth=self.depth,
                height=self.height,
                rotation=self.rotation,
            )

            self.document.recompute()

            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD: błąd wstawiania mebla: "
                f"{error}\n"
            )
            return

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            furniture
        )

        if self.panel is not None:
            self.panel.placement_finished(
                furniture
            )

    def _remove_callback(self):
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

    def stop(
        self,
        close_panel=False,
    ):
        global ACTIVE_FURNITURE_TOOL

        self._remove_callback()

        self.waiting_for_point = False
        self.active = False

        ACTIVE_FURNITURE_TOOL = None

        if (
            close_panel
            and Gui.Control.activeDialog()
        ):
            Gui.Control.closeDialog()


class AddFurnitureCommand:
    """Insert a parametric cabinet."""

    def GetResources(self):
        return {
            "Pixmap": icon("add_cabinet.svg"),
            "MenuText": "Add Cabinet",
            "ToolTip": "Add a parametric cabinet.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        stop_active_tools()

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        tool = FurniturePlacementTool()

        tool.start()


class EditFurnitureCommand:
    """Edit selected furniture."""

    def GetResources(self):
        return {
            "Pixmap": icon("edit_furniture.svg"),
            "MenuText": "Edit Furniture",
            "ToolTip": "Edit dimensions, position and rotation.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        stop_active_tools()

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        furniture = get_selected_furniture(
            "Edytuj mebel"
        )

        if furniture is None:
            return

        panel = FurnitureEditPanel(
            furniture
        )

        Gui.Control.showDialog(
            panel
        )

class MoveFurnitureCommand:
    """Open precise furniture movement panel."""

    def GetResources(self):
        return {
            "Pixmap": icon("move_furniture.svg"),
            "MenuText": "Move Furniture",
            "ToolTip": "Precisely move, nudge, rotate and position furniture.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        stop_active_tools()

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        furniture = get_selected_furniture(
            "Move Furniture"
        )

        if furniture is None:
            return

        panel = FurnitureMovePanel(
            furniture
        )

        Gui.Control.showDialog(
            panel
        )


class SnapFurnitureToWallCommand:
    """Snap furniture back edge to selected wall."""

    def GetResources(self):
        return {
            "Pixmap": icon("snap_wall.svg"),
            "MenuText": "Snap to Wall",
            "ToolTip": "Snap the cabinet back edge to a selected wall.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_SNAP_TOOL

        stop_active_tools()

        furniture = get_selected_furniture(
            "Dosuń do ściany"
        )

        if furniture is None:
            return

        tool = FurnitureSnapWallTool(
            furniture
        )

        ACTIVE_SNAP_TOOL = tool

        tool.start()


class SnapFurnitureToFurnitureCommand:
    """Snap furniture side-to-side."""

    def GetResources(self):
        return {
            "Pixmap": icon("snap_cabinet.svg"),
            "MenuText": "Snap to Cabinet",
            "ToolTip": "Snap the selected cabinet side-to-side with another cabinet.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_SNAP_TOOL

        stop_active_tools()

        furniture = get_selected_furniture(
            "Dosuń do szafki"
        )

        if furniture is None:
            return

        tool = FurnitureSnapFurnitureTool(
            furniture
        )

        ACTIVE_SNAP_TOOL = tool

        tool.start()
class DuplicateFurnitureCommand:
    """Duplicate selected furniture."""

    def GetResources(self):
        return {
            "Pixmap": icon("duplicate_cabinet.svg"),
            "MenuText": "Duplicate Cabinet",
            "ToolTip": "Duplicate the cabinet to the left or right.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        stop_active_tools()

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        furniture = get_selected_furniture(
            "Duplikuj szafkę"
        )

        if furniture is None:
            return

        panel = FurnitureDuplicatePanel(
            furniture
        )

        Gui.Control.showDialog(
            panel
        )

Gui.addCommand(
    "OIC_AddFurniture",
    AddFurnitureCommand(),
)

Gui.addCommand(
    "OIC_EditFurniture",
    EditFurnitureCommand(),
)

Gui.addCommand(
    "OIC_MoveFurniture",
    MoveFurnitureCommand(),
)

Gui.addCommand(
    "OIC_SnapFurnitureWall",
    SnapFurnitureToWallCommand(),
)

Gui.addCommand(
    "OIC_SnapFurnitureFurniture",
    SnapFurnitureToFurnitureCommand(),
)

Gui.addCommand(
    "OIC_DuplicateFurniture",
    DuplicateFurnitureCommand(),
)