"""Floor commands for OpenInteriorCAD."""

import FreeCADGui as Gui
from PySide import QtWidgets

from OICFloor import (
    FLOOR_TYPE,
    ROOM_TYPE,
    create_floor,
)


def find_existing_floor(room):
    """Find floor already assigned to room."""

    document = room.Document

    if document is None:
        return None

    for obj in document.Objects:
        if (
            getattr(
                obj,
                "OICType",
                "",
            )
            != FLOOR_TYPE
        ):
            continue

        if (
            getattr(
                obj,
                "Room",
                None,
            )
            == room
        ):
            return obj

    return None


class AddFloorCommand:
    """Create floor for selected room."""

    def GetResources(self):
        return {
            "MenuText": "Utwórz podłogę",
            "ToolTip": (
                "Tworzy parametryczną podłogę "
                "dla zaznaczonego pomieszczenia."
            ),
        }

    def IsActive(self):
        return True

    def Activated(self):
        selection = (
            Gui.Selection.getSelection()
        )

        if len(selection) != 1:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Utwórz podłogę",
                "Zaznacz jedno pomieszczenie.",
            )
            return

        room = selection[0]

        if (
            getattr(
                room,
                "OICType",
                "",
            )
            != ROOM_TYPE
        ):
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Utwórz podłogę",
                "Zaznaczony obiekt nie jest "
                "pomieszczeniem OpenInteriorCAD.",
            )
            return

        existing = find_existing_floor(
            room
        )

        if existing is not None:
            QtWidgets.QMessageBox.information(
                Gui.getMainWindow(),
                "Utwórz podłogę",
                "To pomieszczenie ma już podłogę.",
            )

            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(
                existing
            )

            return

        document = room.Document

        document.openTransaction(
            "Utwórz podłogę"
        )

        try:
            floor = create_floor(
                document=document,
                room=room,
                thickness=20.0,
            )

            # Dodaj podłogę do grupy pomieszczenia.
            try:
                room.addObject(
                    floor
                )
            except Exception:
                pass

            document.recompute()

            document.commitTransaction()

        except Exception:
            document.abortTransaction()
            raise

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            floor
        )

        try:
            Gui.activeDocument().activeView().fitAll()

        except Exception:
            pass


Gui.addCommand(
    "OIC_AddFloor",
    AddFloorCommand(),
)