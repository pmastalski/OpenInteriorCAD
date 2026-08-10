"""GUI commands for the OpenInteriorCAD workbench."""

import FreeCAD as App
import FreeCADGui as Gui

from OICWall import create_wall


class AddWallCommand:
    """Create a new OpenInteriorCAD wall."""

    def GetResources(self):
        return {
            "MenuText": "Dodaj ścianę",
            "ToolTip": (
                "Dodaje parametryczną ścianę "
                "OpenInteriorCAD do aktywnego dokumentu."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        document = App.ActiveDocument

        if document is None:
            document = App.newDocument(
                "OpenInteriorCAD"
            )

        document.openTransaction(
            "Dodaj ścianę"
        )

        try:
            wall = create_wall(
                document
            )

            document.recompute()

            Gui.activeDocument().activeView().viewAxonometric()
            Gui.activeDocument().activeView().fitAll()

            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(
                wall
            )

            document.commitTransaction()

        except Exception:
            document.abortTransaction()
            raise


Gui.addCommand(
    "OIC_AddWall",
    AddWallCommand(),
)