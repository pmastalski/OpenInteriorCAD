"""Window commands for OpenInteriorCAD."""

import FreeCADGui as Gui
from PySide import QtWidgets

from OICWindowEditPanel import WindowEditPanel
from OICWindowPanel import WindowPanel


class AddWindowCommand:
    """Insert window into selected wall."""

    def GetResources(self):
        return {
            "MenuText": "Dodaj okno",
            "ToolTip": (
                "Dodaje okno do zaznaczonej "
                "ściany OpenInteriorCAD."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Dodaj okno",
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
                "Dodaj okno",
                "Zaznaczony obiekt nie jest ścianą.",
            )

            return

        panel = WindowPanel(
            wall
        )

        Gui.Control.showDialog(
            panel
        )


class EditWindowCommand:
    """Edit selected OpenInteriorCAD window."""

    def GetResources(self):
        return {
            "MenuText": "Edytuj okno",
            "ToolTip": (
                "Edytuje wymiary i położenie "
                "zaznaczonego okna."
            ),
        }

    def IsActive(self):
        # Celowo zawsze aktywne.
        # Unikamy problemu z odświeżaniem
        # stanu komendy po zmianie zaznaczenia.
        return True

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        selection = Gui.Selection.getSelection()

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Edytuj okno",
                "Zaznacz dokładnie jedno okno.",
            )

            return

        window = selection[0]

        if (
            getattr(
                window,
                "OICType",
                "",
            )
            != "OpenInteriorCAD::Window"
        ):
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Edytuj okno",
                "Zaznaczony obiekt nie jest oknem.",
            )

            return

        panel = WindowEditPanel(
            window
        )

        Gui.Control.showDialog(
            panel
        )


Gui.addCommand(
    "OIC_AddWindow",
    AddWindowCommand(),
)

Gui.addCommand(
    "OIC_EditWindow",
    EditWindowCommand(),
)