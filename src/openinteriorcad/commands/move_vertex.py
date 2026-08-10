from openinteriorcad.commands.base import Command
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.geometry.point2d import Point2D


class MoveVertexCommand(Command):
    """Moves a vertex while preserving its previous position."""

    def __init__(
        self,
        vertex: Vertex2D,
        new_position: Point2D,
    ) -> None:
        self.vertex = vertex
        self.new_position = new_position
        self.old_position = vertex.position

    def execute(self) -> None:
        self.vertex.position = self.new_position

    def undo(self) -> None:
        self.vertex.position = self.old_position