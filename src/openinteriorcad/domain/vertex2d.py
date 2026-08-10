from dataclasses import dataclass, field
from uuid import UUID, uuid4

from openinteriorcad.geometry.point2d import Point2D


@dataclass
class Vertex2D:
    """Topological 2D vertex shared by connected semantic objects."""

    position: Point2D
    id: UUID = field(default_factory=uuid4)