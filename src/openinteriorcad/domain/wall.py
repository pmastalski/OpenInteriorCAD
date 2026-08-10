from dataclasses import dataclass, field

from openinteriorcad.core.entity import Entity
from openinteriorcad.geometry.point2d import Point2D


@dataclass
class Wall(Entity):
    """Semantic wall object."""

    start: Point2D = field(
        default_factory=lambda: Point2D(0.0, 0.0)
    )

    end: Point2D = field(
        default_factory=lambda: Point2D(1000.0, 0.0)
    )

    thickness: float = 120.0
    height: float = 2600.0

    def __post_init__(self):
        super().__post_init__()

        if self.start == self.end:
            raise ValueError(
                "Wall start and end points cannot be identical."
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
    def length(self) -> float:
        return self.start.distance_to(self.end)