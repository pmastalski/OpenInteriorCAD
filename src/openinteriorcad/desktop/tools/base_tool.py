from abc import ABC

from PySide6.QtCore import QPointF


class BaseTool(ABC):
    """Base class for interactive desktop tools."""

    name = "Base"

    def __init__(self, view) -> None:
        self.view = view

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def mouse_press(
        self,
        position: QPointF,
    ) -> None:
        pass

    def mouse_move(
        self,
        position: QPointF,
    ) -> None:
        pass

    def cancel(self) -> None:
        pass