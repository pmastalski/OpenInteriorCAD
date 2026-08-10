from dataclasses import dataclass, field

from openinteriorcad.core.entity import Entity
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.geometry.point2d import Point2D


@dataclass
class Wall(Entity):
    """Semantic wall defined by two shared vertices."""

    start_vertex: Vertex2D = field(
        default_factory=lambda: Vertex2D(
            position=Point2D(0.0, 0.0)
        )
    )

    end_vertex: Vertex2D = field(
        default_factory=lambda: Vertex2D(
            position=Point2D(1000.0, 0.0)
        )
    )

    thickness: float = 120.0
    height: float = 2600.0

    def __post_init__(self):
        super().__post_init__()

        if self.start_vertex.id == self.end_vertex.id:
            raise ValueError(
                "Wall start and end vertices cannot be identical."
            )

        if self.start == self.end:
            raise ValueError(
                "Wall start and end positions cannot be identical."
            )

        if self.thickness <= 0:
            raise ValueError(
                "Wall thickness must be greater than zero."
            )

        if self.height <= 0:
            raise ValueError(
                "Wall height must be greater than zero."
            )

    @property
    def start(self) -> Point2D:
        return self.start_vertex.position

    @property
    def end(self) -> Point2D:
        return self.end_vertex.position

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)