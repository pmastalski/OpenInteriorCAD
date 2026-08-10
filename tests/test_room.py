from openinteriorcad.domain.room import Room
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


def create_rectangular_room():
    p1 = Point2D(0, 0)
    p2 = Point2D(4000, 0)
    p3 = Point2D(4000, 3000)
    p4 = Point2D(0, 3000)

    room = Room(name="Kitchen")

    room.add_wall(
        Wall(name="Wall 1", start=p1, end=p2)
    )

    room.add_wall(
        Wall(name="Wall 2", start=p2, end=p3)
    )

    room.add_wall(
        Wall(name="Wall 3", start=p3, end=p4)
    )

    room.add_wall(
        Wall(name="Wall 4", start=p4, end=p1)
    )

    return room


def test_room_has_four_walls():
    room = create_rectangular_room()

    assert room.wall_count == 4


def test_rectangular_room_is_closed():
    room = create_rectangular_room()

    assert room.is_closed is True


def test_incomplete_room_is_not_closed():
    room = create_rectangular_room()

    room.walls.pop()

    assert room.is_closed is False