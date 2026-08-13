"""Furniture commands for OpenInteriorCAD."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICFurniture import create_furniture
from OICFurnitureEditPanel import FurnitureEditPanel
from OICFurnitureMove import FurnitureMoveTool
from OICFurniturePanel import FurniturePanel


ACTIVE_FURNITURE_TOOL = None
ACTIVE_MOVE_TOOL = None


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
    """Insert parametric cabinet."""

    def GetResources(self):
        return {
            "MenuText": "Wstaw szafkę",
            "ToolTip": (
                "Wstawia parametryczną szafkę."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_FURNITURE_TOOL

        if (
            ACTIVE_FURNITURE_TOOL is not None
            and ACTIVE_FURNITURE_TOOL.active
        ):
            ACTIVE_FURNITURE_TOOL.stop(
                close_panel=True
            )

            return

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        tool = FurniturePlacementTool()

        tool.start()


class EditFurnitureCommand:
    """Edit selected furniture."""

    def GetResources(self):
        return {
            "MenuText": "Edytuj mebel",
            "ToolTip": (
                "Edytuje wymiary, położenie "
                "i obrót mebla."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_FURNITURE_TOOL

        if (
            ACTIVE_FURNITURE_TOOL is not None
            and ACTIVE_FURNITURE_TOOL.active
        ):
            ACTIVE_FURNITURE_TOOL.stop(
                close_panel=True
            )

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Edytuj mebel",
                "Zaznacz dokładnie jeden mebel.",
            )

            return

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
                "Edytuj mebel",
                "Zaznaczony obiekt nie jest meblem.",
            )

            return

        panel = FurnitureEditPanel(
            furniture
        )

        Gui.Control.showDialog(
            panel
        )


class MoveFurnitureCommand:
    """Move selected furniture interactively."""

    def GetResources(self):
        return {
            "MenuText": "Przesuń mebel",
            "ToolTip": (
                "Przesuwa zaznaczony mebel "
                "i przyciąga go do ściany."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        global ACTIVE_MOVE_TOOL
        global ACTIVE_FURNITURE_TOOL

        if (
            ACTIVE_FURNITURE_TOOL is not None
            and ACTIVE_FURNITURE_TOOL.active
        ):
            ACTIVE_FURNITURE_TOOL.stop(
                close_panel=True
            )

        if (
            ACTIVE_MOVE_TOOL is not None
            and ACTIVE_MOVE_TOOL.active
        ):
            ACTIVE_MOVE_TOOL.stop()
            ACTIVE_MOVE_TOOL = None

            return

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Przesuń mebel",
                "Zaznacz dokładnie jeden mebel.",
            )

            return

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
                "Przesuń mebel",
                "Zaznaczony obiekt nie jest meblem.",
            )

            return

        tool = FurnitureMoveTool(
            furniture
        )

        ACTIVE_MOVE_TOOL = tool

        tool.start()


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