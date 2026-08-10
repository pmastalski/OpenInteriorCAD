from openinteriorcad.commands.base import Command
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.wall import Wall


class AddWallCommand(Command):
    """Adds a wall to a room with undo/redo support."""

    def __init__(
        self,
        room: Room,
        wall: Wall,
    ) -> None:
        self.room = room
        self.wall = wall

    def execute(self) -> None:
        self.room.add_wall(
            self.wall
        )

    def undo(self) -> None:
        self.room.remove_wall(
            self.wall
        )