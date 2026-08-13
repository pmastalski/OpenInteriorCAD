"""Free furniture movement with live preview."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui


class FurnitureMoveTool:
    """Free interactive furniture movement."""

    def __init__(self, furniture):
        self.furniture = furniture
        self.document = furniture.Document

        self.view = None
        self.mouse_callback = None
        self.move_callback = None
        self.escape_shortcut = None

        self.active = False

        self.original_position = App.Vector(
            furniture.Position.x,
            furniture.Position.y,
            furniture.Position.z,
        )

        self.original_rotation = furniture.RotationAngle.Value

        self.preview_position = App.Vector(
            self.original_position.x,
            self.original_position.y,
            self.original_position.z,
        )

    def start(self):
        gui_document = Gui.activeDocument()

        if gui_document is None:
            return

        self.view = gui_document.activeView()
        self.active = True

        self.mouse_callback = self.view.addEventCallback(
            "SoMouseButtonEvent",
            self._mouse_event,
        )

        self.move_callback = self.view.addEventCallback(
            "SoLocation2Event",
            self._move_event,
        )

        main_window = Gui.getMainWindow()

        self.escape_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Esc"),
            main_window,
        )

        self.escape_shortcut.setContext(
            QtCore.Qt.ShortcutContext.ApplicationShortcut
        )

        self.escape_shortcut.activated.connect(
            self.cancel
        )

        try:
            main_window.statusBar().showMessage(
                "OpenInteriorCAD: przesuwaj mebel kursorem. "
                "Kliknij = zatwierdź. Esc = anuluj."
            )
        except Exception:
            pass

    def _get_world_point(self, info):
        position = info.get("Position")

        if position is None:
            return None

        try:
            point = self.view.getPoint(
                position[0],
                position[1],
            )
        except Exception:
            return None

        return App.Vector(
            point.x,
            point.y,
            self.original_position.z,
        )

    def _move_event(self, info):
        if not self.active:
            return

        point = self._get_world_point(info)

        if point is None:
            return

        self.preview_position = point

        self.furniture.Position = App.Vector(
            point.x,
            point.y,
            point.z,
        )

        self.furniture.RotationAngle = self.original_rotation

        self.document.recompute()

        try:
            self.view.redraw()
        except Exception:
            pass

    def _mouse_event(self, info):
        if not self.active:
            return

        if info.get("State") != "DOWN":
            return

        if info.get("Button") != "BUTTON1":
            return

        self.document.openTransaction(
            "Przesuń mebel"
        )

        try:
            self.furniture.Position = App.Vector(
                self.preview_position.x,
                self.preview_position.y,
                self.preview_position.z,
            )

            self.document.recompute()
            self.document.commitTransaction()

        except Exception as error:
            self.document.abortTransaction()

            App.Console.PrintError(
                "OpenInteriorCAD move error: "
                f"{error}\n"
            )

            return

        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(
            self.furniture
        )

        self.stop()

    def cancel(self):
        if not self.active:
            return

        self.furniture.Position = App.Vector(
            self.original_position.x,
            self.original_position.y,
            self.original_position.z,
        )

        self.furniture.RotationAngle = (
            self.original_rotation
        )

        self.document.recompute()

        try:
            self.view.redraw()
        except Exception:
            pass

        self.stop()

    def stop(self):
        if self.view is not None:
            if self.mouse_callback is not None:
                try:
                    self.view.removeEventCallback(
                        "SoMouseButtonEvent",
                        self.mouse_callback,
                    )
                except Exception:
                    pass

            if self.move_callback is not None:
                try:
                    self.view.removeEventCallback(
                        "SoLocation2Event",
                        self.move_callback,
                    )
                except Exception:
                    pass

        self.mouse_callback = None
        self.move_callback = None

        if self.escape_shortcut is not None:
            try:
                self.escape_shortcut.setEnabled(False)
                self.escape_shortcut.deleteLater()
            except Exception:
                pass

        self.escape_shortcut = None
        self.active = False

        try:
            Gui.getMainWindow().statusBar().clearMessage()
        except Exception:
            pass