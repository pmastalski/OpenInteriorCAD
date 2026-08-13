"""GUI initialization for the OpenInteriorCAD workbench."""

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
        import OICCommands
        import OICFloorCommands
        import OICFurnitureCommands
        import OICWindowCommands

        self.command_list = [
            "OIC_DrawRoomV2",
            "OIC_EditWallV2",
            "OIC_AddDoor",
            "OIC_EditDoor",
            "OIC_AddWindow",
            "OIC_EditWindow",
            "OIC_AddFloor",
            "OIC_AddFurniture",
            "OIC_EditFurniture",
            "OIC_MoveFurniture",
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