"""GUI initialization for the OpenInteriorCAD workbench."""

import importlib

import FreeCADGui as Gui


class OpenInteriorCADWorkbench(Gui.Workbench):
    """OpenInteriorCAD FreeCAD workbench."""

    MenuText = "OpenInteriorCAD"

    ToolTip = (
        "Interior and furniture design with "
        "parametric OpenInteriorCAD objects."
    )

    Icon = ""

    def Initialize(self):
        """Register OpenInteriorCAD commands."""

        import OICCommands
        import OICWindowCommands
        import OICFloorCommands
        import OICFurnitureCommands
        import OICCabinetRunCommands

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

        if (
            "OIC_CreateCabinetRun"
            not in Gui.listCommands()
        ):
            importlib.reload(
                OICCabinetRunCommands
            )

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
            "OIC_SnapFurnitureWall",
            "OIC_SnapFurnitureFurniture",
            "OIC_DuplicateFurniture",

            # Cabinet Run
            "OIC_CreateCabinetRun",
            "OIC_MoveCabinetRun",
            "OIC_UngroupCabinetRun",
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
        pass

    def Deactivated(self):
        pass

    def ContextMenu(
        self,
        recipient,
    ):
        self.appendContextMenu(
            "OpenInteriorCAD",
            self.command_list,
        )

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(
    OpenInteriorCADWorkbench()
)
