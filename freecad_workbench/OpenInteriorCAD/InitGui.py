"""GUI initialization for the OpenInteriorCAD workbench."""

import importlib

import FreeCADGui as Gui


class OpenInteriorCADWorkbench(
    Gui.Workbench
):
    """OpenInteriorCAD FreeCAD workbench."""

    MenuText = "OpenInteriorCAD"

    ToolTip = (
        "Interior and furniture design with "
        "parametric OpenInteriorCAD objects."
    )

    Icon = ""

    def Initialize(
        self,
    ):
        """Register OpenInteriorCAD commands."""

        # --------------------------------------------------
        # ARCHITECTURE
        # --------------------------------------------------

        import OICCommands

        # --------------------------------------------------
        # WINDOWS
        # --------------------------------------------------

        import OICWindowCommands

        # --------------------------------------------------
        # FLOOR
        # --------------------------------------------------

        import OICFloorCommands

        # --------------------------------------------------
        # FURNITURE
        # --------------------------------------------------

        import OICFurnitureCommands

        # FreeCAD can retain an older development module in sys.modules.
        commands = Gui.listCommands()

        if (
            "OIC_SnapFurnitureWall"
            not in commands
            or
            "OIC_SnapFurnitureFurniture"
            not in commands
            or
            "OIC_CutList"
            not in commands
            or
            "OIC_EdgeAssignment"
            not in commands
        ):
            importlib.reload(
                OICFurnitureCommands
            )

        # --------------------------------------------------
        # TOOLBAR / MENU
        # --------------------------------------------------

        self.command_list = [
            # Room
            "OIC_DrawRoomV2",
            "OIC_EditWallV2",

            # Doors
            "OIC_AddDoor",
            "OIC_EditDoor",

            # Windows
            "OIC_AddWindow",
            "OIC_EditWindow",

            # Floor
            "OIC_AddFloor",

            # Furniture
            "OIC_AddFurniture",
            "OIC_EditFurniture",
            "OIC_MoveFurniture",

            # Dedicated snapping tools
            "OIC_SnapFurnitureWall",
            "OIC_SnapFurnitureFurniture",
            "OIC_DuplicateFurniture",

            # Production
            "OIC_EdgeAssignment",
            "OIC_CutList",
        ]

        self.appendToolbar(
            "OpenInteriorCAD",
            self.command_list,
        )

        self.appendMenu(
            "OpenInteriorCAD",
            self.command_list,
        )

    def Activated(
        self,
    ):
        """Called when workbench becomes active."""

        pass

    def Deactivated(
        self,
    ):
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

    def GetClassName(
        self,
    ):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(
    OpenInteriorCADWorkbench()
)
