"""Cabinet Run commands for OpenInteriorCAD."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from OICCabinetRun import (
    RUN_TYPE, create_cabinet_run, dissolve_cabinet_run, ensure_run_properties,
)
from OICCabinetRunEditPanel import CabinetRunEditPanel
from OICCabinetRunMovePanel import CabinetRunMovePanel
from OICCabinetRunSnapWallPanel import CabinetRunSnapWallPanel
from OICIcons import icon


def get_selected_run(title):
    selection = Gui.Selection.getSelection()
    if len(selection) != 1:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(), title, "Select exactly one Cabinet Run."
        )
        return None
    run = selection[0]
    if getattr(run, "OICType", "") != RUN_TYPE:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(), title, "The selected object is not a Cabinet Run."
        )
        return None
    ensure_run_properties(run)
    return run


class CreateCabinetRunCommand:
    def GetResources(self):
        return {
            "Pixmap": icon("create_cabinet_run.svg"),
            "MenuText": "Create Cabinet Run",
            "ToolTip": "Create a run from two or more selected cabinets.",
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        cabinets = [
            obj for obj in Gui.Selection.getSelection()
            if getattr(obj, "OICType", "") == "OpenInteriorCAD::Furniture"
        ]
        if len(cabinets) < 2:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(), "Create Cabinet Run",
                "Select at least two cabinets."
            )
            return
        doc = App.ActiveDocument
        doc.openTransaction("Create Cabinet Run")
        try:
            run = create_cabinet_run(doc, cabinets)
            doc.commitTransaction()
        except Exception as error:
            doc.abortTransaction()
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(), "Create Cabinet Run", str(error)
            )
            return
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(run)


class EditCabinetRunCommand:
    def GetResources(self):
        return {
            "Pixmap": icon("edit_cabinet_run.svg"),
            "MenuText": "Edit Cabinet Run",
            "ToolTip": "Arrange cabinets, set gaps and align fronts.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()
        run = get_selected_run("Edit Cabinet Run")
        if run is not None:
            Gui.Control.showDialog(CabinetRunEditPanel(run))


class MoveCabinetRunCommand:
    def GetResources(self):
        return {
            "Pixmap": icon("move_cabinet_run.svg"),
            "MenuText": "Move Cabinet Run",
            "ToolTip": "Move all cabinets in the selected run together.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()
        run = get_selected_run("Move Cabinet Run")
        if run is not None:
            Gui.Control.showDialog(CabinetRunMovePanel(run))


class SnapCabinetRunWallCommand:
    def GetResources(self):
        return {
            "Pixmap": icon("snap_run_wall.svg"),
            "MenuText": "Snap Run to Wall",
            "ToolTip": "Snap the complete Cabinet Run to a wall with an offset.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()
        run = get_selected_run("Snap Run to Wall")
        if run is not None:
            Gui.Control.showDialog(CabinetRunSnapWallPanel(run))


class UngroupCabinetRunCommand:
    def GetResources(self):
        return {
            "Pixmap": icon("ungroup_cabinet_run.svg"),
            "MenuText": "Ungroup Cabinet Run",
            "ToolTip": "Remove the run group without deleting cabinets.",
        }

    def IsActive(self):
        return True

    def Activated(self):
        run = get_selected_run("Ungroup Cabinet Run")
        if run is None:
            return
        doc = run.Document
        doc.openTransaction("Ungroup Cabinet Run")
        try:
            dissolve_cabinet_run(run)
            doc.commitTransaction()
        except Exception as error:
            doc.abortTransaction()
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(), "Ungroup Cabinet Run", str(error)
            )


Gui.addCommand("OIC_CreateCabinetRun", CreateCabinetRunCommand())
Gui.addCommand("OIC_EditCabinetRun", EditCabinetRunCommand())
Gui.addCommand("OIC_MoveCabinetRun", MoveCabinetRunCommand())
Gui.addCommand("OIC_SnapCabinetRunWall", SnapCabinetRunWallCommand())
Gui.addCommand("OIC_UngroupCabinetRun", UngroupCabinetRunCommand())
