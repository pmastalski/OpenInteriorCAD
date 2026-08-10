from dataclasses import dataclass, field

from openinteriorcad.core.entity import Entity
from openinteriorcad.domain.wall import Wall


@dataclass
class Room(Entity):
    """Semantic room consisting of walls."""

    walls: list[Wall] = field(default_factory=list)

    def add_wall(self, wall: Wall) -> None:
        if any(
            existing_wall.id == wall.id
            for existing_wall in self.walls
        ):
            raise ValueError(
                f"Wall {wall.id} already exists in room."
            )

        self.walls.append(wall)

    def remove_wall(self, wall: Wall) -> None:
        self.walls.remove(wall)

    @property
    def wall_count(self) -> int:
        return len(self.walls)

    @property
    def is_closed(self) -> bool:
        if len(self.walls) < 3:
            return False

        for current, following in zip(
            self.walls,
            self.walls[1:],
        ):
            if current.end != following.start:
                return False

        return self.walls[-1].end == self.walls[0].start