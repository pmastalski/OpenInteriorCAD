"""Commands for standalone OpenInteriorCAD filler elements."""

from __future__ import annotations

import FreeCAD as App
import FreeCADGui as Gui

from OICBoardElement import OIC_TYPE, create_filler
from OICBoardElementPanel import BoardElementEditPanel


class AddFillerCommand:
    def GetResources(self):
        return {
            "MenuText": "Add Filler",
            "ToolTip": (
                "Add a standalone parametric filler / board element with "
                "selectable edge banding."
            ),
        }

    def Activated(self):
        if App.ActiveDocument is None:
            App.newDocument("OpenInteriorCAD")

        obj = create_filler(
            document=App.ActiveDocument,
            name="Filler",
        )

        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(obj)

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        Gui.Control.showDialog(
            BoardElementEditPanel(obj)
        )

    def IsActive(self):
        return True


class EditFillerCommand:
    def GetResources(self):
        return {
            "MenuText": "Edit Filler",
            "ToolTip": "Edit a selected OpenInteriorCAD filler element.",
        }

    def Activated(self):
        selection = [
            obj
            for obj in Gui.Selection.getSelection()
            if getattr(obj, "OICType", "") == OIC_TYPE
        ]

        if not selection:
            App.Console.PrintWarning(
                "Select an OpenInteriorCAD filler first.\n"
            )
            return

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        Gui.Control.showDialog(
            BoardElementEditPanel(selection[0])
        )

    def IsActive(self):
        return App.ActiveDocument is not None


Gui.addCommand(
    "OIC_AddFiller",
    AddFillerCommand(),
)

Gui.addCommand(
    "OIC_EditFiller",
    EditFillerCommand(),
)
