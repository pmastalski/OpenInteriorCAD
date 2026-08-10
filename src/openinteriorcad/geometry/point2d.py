from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class Point2D:
    """Immutable 2D point expressed in millimetres."""

    x: float
    y: float

    def distance_to(self, other: "Point2D") -> float:
        return hypot(
            other.x - self.x,
            other.y - self.y,
        )