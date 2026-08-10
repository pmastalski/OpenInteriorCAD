from openinteriorcad.commands.add_wall import AddWallCommand
from openinteriorcad.commands.history import CommandHistory
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


def test_add_wall_command_supports_undo_redo():
    room = Room(
        name="Room"
    )

    wall = Wall(
        name="Wall",
        start_vertex=Vertex2D(
            position=Point2D(0, 0)
        ),
        end_vertex=Vertex2D(
            position=Point2D(4000, 0)
        ),
    )

    history = CommandHistory()

    history.execute(
        AddWallCommand(
            room,
            wall,
        )
    )

    assert room.wall_count == 1

    history.undo()

    assert room.wall_count == 0

    history.redo()

    assert room.wall_count == 1