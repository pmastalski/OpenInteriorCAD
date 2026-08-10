from PySide6.QtCore import QPointF
from PySide6.QtGui import QPen

from openinteriorcad.commands.add_wall import AddWallCommand
from openinteriorcad.desktop.tools.base_tool import BaseTool
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall


class WallTool(BaseTool):
    """Interactive wall drawing tool."""

    name = "Wall"

    def __init__(self, view) -> None:
        super().__init__(
            view
        )

        self.start_vertex: Vertex2D | None = None
        self.preview_item = None

    def activate(self) -> None:
        self.start_vertex = None

    def deactivate(self) -> None:
        self.cancel()

    def mouse_press(
        self,
        position: QPointF,
    ) -> None:
        if self.start_vertex is None:
            self.start_vertex = (
                self.view.get_or_create_vertex(
                    position
                )
            )

            return

        end_vertex = (
            self.view.get_or_create_vertex(
                position
            )
        )

        if end_vertex.id == self.start_vertex.id:
            return

        if (
            end_vertex.position
            == self.start_vertex.position
        ):
            return

        wall = Wall(
            name=(
                f"Wall "
                f"{self.view.room.wall_count + 1}"
            ),
            start_vertex=self.start_vertex,
            end_vertex=end_vertex,
        )

        command = AddWallCommand(
            self.view.room,
            wall,
        )

        self.view.command_history.execute(
            command
        )

        self._remove_preview()

        self.start_vertex = end_vertex

        self.view.render_room(
            self.view.room
        )

    def mouse_move(
        self,
        position: QPointF,
    ) -> None:
        if self.start_vertex is None:
            return

        end_point = self.view.snap_position(
            position
        )

        self._draw_preview(
            end_point.x,
            end_point.y,
        )

    def cancel(self) -> None:
        self.start_vertex = None

        self._remove_preview()

    def _draw_preview(
        self,
        x: float,
        y: float,
    ) -> None:
        self._remove_preview()

        if self.start_vertex is None:
            return

        pen = QPen()
        pen.setWidthF(
            15
        )

        self.preview_item = (
            self.view.graphics_scene.addLine(
                self.start_vertex.position.x,
                self.start_vertex.position.y,
                x,
                y,
                pen,
            )
        )

        self.preview_item.setZValue(
            100
        )

    def _remove_preview(self) -> None:
        if self.preview_item is None:
            return

        if (
            self.preview_item.scene()
            is not None
        ):
            self.view.graphics_scene.removeItem(
                self.preview_item
            )

        self.preview_item = None