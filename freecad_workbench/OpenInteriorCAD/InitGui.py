"""GUI initialization for the OpenInteriorCAD workbench."""

import importlib

import FreeCADGui as Gui


class OpenInteriorCADWorkbench(Gui.Workbench):
    """OpenInteriorCAD FreeCAD workbench."""

    MenuText = "OpenInteriorCAD"

    ToolTip = (
        "Projektowanie wnętrz i mebli "
        "z wykorzystaniem inteligentnych obiektów."
    )

    Icon = ""

    def Initialize(self):
        """Register OpenInteriorCAD commands."""

        # --------------------------------------------------
        # ARCHITEKTURA
        # --------------------------------------------------

        import OICCommands

        # --------------------------------------------------
        # OKNA
        # --------------------------------------------------

        import OICWindowCommands

        # --------------------------------------------------
        # PODŁOGA
        # --------------------------------------------------

        import OICFloorCommands

        # --------------------------------------------------
        # MEBLE
        # --------------------------------------------------

        import OICFurnitureCommands

        # Podczas rozwoju Workbencha FreeCAD potrafi
        # pozostawić starszą wersję modułu w sys.modules.
        #
        # Jeżeli nowe komendy nie zostały zarejestrowane,
        # przeładuj moduł meblowy.
        commands = Gui.listCommands()

        if (
            "OIC_SnapFurnitureWall"
            not in commands
            or
            "OIC_SnapFurnitureFurniture"
            not in commands
        ):
            importlib.reload(
                OICFurnitureCommands
            )

        # --------------------------------------------------
        # TOOLBAR / MENU
        # --------------------------------------------------

        self.command_list = [
            # Pomieszczenie
            "OIC_DrawRoomV2",
            "OIC_EditWallV2",

            # Drzwi
            "OIC_AddDoor",
            "OIC_EditDoor",

            # Okna
            "OIC_AddWindow",
            "OIC_EditWindow",

            # Podłoga
            "OIC_AddFloor",

            # Meble
            "OIC_AddFurniture",
            "OIC_EditFurniture",
            "OIC_MoveFurniture",

            # Osobne operacje dosuwania
            "OIC_SnapFurnitureWall",
            "OIC_SnapFurnitureFurniture",
            "OIC_DuplicateFurniture",
        ]

        self.appendToolbar(
            "OpenInteriorCAD",
            self.command_list,
        )

        self.appendMenu(
            "OpenInteriorCAD",
            self.command_list,
        )

    def Activated(self):
        """Called when workbench becomes active."""

        pass

    def Deactivated(self):
        """Called when leaving workbench."""

        pass

    def ContextMenu(
        self,
        recipient,
    ):
        """Add OpenInteriorCAD context menu."""

        self.appendContextMenu(
            "OpenInteriorCAD",
            self.command_list,
        )

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(
    OpenInteriorCADWorkbench()
)