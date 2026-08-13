"""Cabinet Run commands for OpenInteriorCAD."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICCabinetRun import (
    RUN_TYPE,
    create_cabinet_run,
    dissolve_cabinet_run,
)
from OICCabinetRunMovePanel import (
    CabinetRunMovePanel,
)
from OICIcons import icon


def get_selected_run(
    title,
):
    selection = Gui.Selection.getSelection()

    if len(selection) != 1:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(),
            title,
            "Select exactly one Cabinet Run.",
        )
        return None

    run = selection[0]

    if getattr(
        run,
        "OICType",
        "",
    ) != RUN_TYPE:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(),
            title,
            "The selected object is not a Cabinet Run.",
        )
        return None

    return run


class CreateCabinetRunCommand:
    """Create a logical run from selected cabinets."""

    def GetResources(self):
        return {
            "Pixmap": icon(
                "create_cabinet_run.svg"
            ),
            "MenuText": "Create Cabinet Run",
            "ToolTip": (
                "Create a logical run from "
                "two or more selected cabinets."
            ),
        }

    def IsActive(self):
        return (
            App.ActiveDocument
            is not None
        )

    def Activated(self):
        selection = Gui.Selection.getSelection()

        cabinets = [
            obj
            for obj in selection
            if getattr(
                obj,
                "OICType",
                "",
            )
            == "OpenInteriorCAD::Furniture"
        ]

        if len(cabinets) < 2:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Create Cabinet Run",
                "Select at least two cabinets.",
            )
            return

        document = App.ActiveDocument

        document.openTransaction(
            "Create Cabinet Run"
        )

        try:
            run = create_cabinet_run(
                document,
                cabinets,
            )

            document.commitTransaction()

        except Exception as error:
            document.abortTransaction()

            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Create Cabinet Run",
                str(error),
            )
            return

        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(
            run
        )


class MoveCabinetRunCommand:
    """Move all cabinets in the selected run."""

    def GetResources(self):
        return {
            "Pixmap": icon(
                "move_cabinet_run.svg"
            ),
            "MenuText": "Move Cabinet Run",
            "ToolTip": (
                "Move all cabinets in the "
                "selected run together."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        run = get_selected_run(
            "Move Cabinet Run"
        )

        if run is None:
            return

        Gui.Control.showDialog(
            CabinetRunMovePanel(
                run
            )
        )


class UngroupCabinetRunCommand:
    """Remove the run group but keep the cabinets."""

    def GetResources(self):
        return {
            "Pixmap": icon(
                "ungroup_cabinet_run.svg"
            ),
            "MenuText": "Ungroup Cabinet Run",
            "ToolTip": (
                "Remove the Cabinet Run group "
                "without deleting its cabinets."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        run = get_selected_run(
            "Ungroup Cabinet Run"
        )

        if run is None:
            return

        document = run.Document

        document.openTransaction(
            "Ungroup Cabinet Run"
        )

        try:
            dissolve_cabinet_run(
                run
            )

            document.commitTransaction()

        except Exception as error:
            document.abortTransaction()

            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Ungroup Cabinet Run",
                str(error),
            )


Gui.addCommand(
    "OIC_CreateCabinetRun",
    CreateCabinetRunCommand(),
)

Gui.addCommand(
    "OIC_MoveCabinetRun",
    MoveCabinetRunCommand(),
)

Gui.addCommand(
    "OIC_UngroupCabinetRun",
    UngroupCabinetRunCommand(),
)
