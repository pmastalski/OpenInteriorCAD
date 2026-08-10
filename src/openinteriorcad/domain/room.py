from dataclasses import dataclass, field

from openinteriorcad.core.entity import Entity
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall


@dataclass
class Room(Entity):
    """Semantic room consisting of connected walls."""

    vertices: list[Vertex2D] = field(default_factory=list)
    walls: list[Wall] = field(default_factory=list)

    def add_vertex(self, vertex: Vertex2D) -> None:
        if any(
            existing.id == vertex.id
            for existing in self.vertices
        ):
            raise ValueError(
                f"Vertex {vertex.id} already exists in room."
            )

        self.vertices.append(vertex)

    def add_wall(self, wall: Wall) -> None:
        if any(
            existing.id == wall.id
            for existing in self.walls
        ):
            raise ValueError(
                f"Wall {wall.id} already exists in room."
            )

        self.walls.append(wall)

        if not any(
            vertex.id == wall.start_vertex.id
            for vertex in self.vertices
        ):
            self.vertices.append(wall.start_vertex)

        if not any(
            vertex.id == wall.end_vertex.id
            for vertex in self.vertices
        ):
            self.vertices.append(wall.end_vertex)

    def remove_wall(self, wall: Wall) -> None:
        self.walls.remove(wall)

    @property
    def wall_count(self) -> int:
        return len(self.walls)

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def is_closed(self) -> bool:
        if len(self.walls) < 3:
            return False

        vertex_usage: dict[object, int] = {}

        for wall in self.walls:
            for vertex in (
                wall.start_vertex,
                wall.end_vertex,
            ):
                vertex_usage[vertex.id] = (
                    vertex_usage.get(vertex.id, 0) + 1
                )

        return all(
            usage == 2
            for usage in vertex_usage.values()
        )