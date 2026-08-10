from openinteriorcad.commands.history import CommandHistory
from openinteriorcad.commands.move_vertex import MoveVertexCommand
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


def make_vertex(x, y):
    return Vertex2D(
        position=Point2D(x, y)
    )


def create_rectangular_room():
    v1 = make_vertex(0, 0)
    v2 = make_vertex(4000, 0)
    v3 = make_vertex(4000, 3000)
    v4 = make_vertex(0, 3000)

    room = Room(name="Kitchen")

    room.add_wall(
        Wall(
            name="Wall 1",
            start_vertex=v1,
            end_vertex=v2,
        )
    )

    room.add_wall(
        Wall(
            name="Wall 2",
            start_vertex=v2,
            end_vertex=v3,
        )
    )

    room.add_wall(
        Wall(
            name="Wall 3",
            start_vertex=v3,
            end_vertex=v4,
        )
    )

    room.add_wall(
        Wall(
            name="Wall 4",
            start_vertex=v4,
            end_vertex=v1,
        )
    )

    return room


def test_room_has_four_walls():
    room = create_rectangular_room()

    assert room.wall_count == 4


def test_room_has_four_vertices():
    room = create_rectangular_room()

    assert room.vertex_count == 4


def test_rectangular_room_is_closed():
    room = create_rectangular_room()

    assert room.is_closed is True


def test_incomplete_room_is_not_closed():
    room = create_rectangular_room()

    room.walls.pop()

    assert room.is_closed is False


def test_shared_vertex_updates_two_walls():
    room = create_rectangular_room()

    wall_1 = room.walls[0]
    wall_2 = room.walls[1]

    shared_vertex = wall_1.end_vertex

    assert shared_vertex.id == wall_2.start_vertex.id

    shared_vertex.position = Point2D(4500, 0)

    assert wall_1.length == 4500
    assert wall_2.start == Point2D(4500, 0)

def test_move_vertex_command_updates_connected_walls():
    room = create_rectangular_room()

    wall_1 = room.walls[0]
    wall_2 = room.walls[1]

    shared_vertex = wall_1.end_vertex

    history = CommandHistory()

    history.execute(
        MoveVertexCommand(
            shared_vertex,
            Point2D(4500, 0),
        )
    )

    assert wall_1.length == 4500
    assert wall_2.start == Point2D(4500, 0)

    history.undo()

    assert wall_1.length == 4000
    assert wall_2.start == Point2D(4000, 0)