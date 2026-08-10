import pytest

from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


def make_vertex(x, y):
    return Vertex2D(
        position=Point2D(x, y)
    )


def test_wall_length():
    wall = Wall(
        name="Wall 1",
        start_vertex=make_vertex(0, 0),
        end_vertex=make_vertex(4000, 0),
    )

    assert wall.length == 4000


def test_diagonal_wall_length():
    wall = Wall(
        name="Diagonal wall",
        start_vertex=make_vertex(0, 0),
        end_vertex=make_vertex(3000, 4000),
    )

    assert wall.length == pytest.approx(5000)


def test_zero_length_wall_is_rejected():
    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start_vertex=make_vertex(1000, 1000),
            end_vertex=make_vertex(1000, 1000),
        )


def test_same_vertex_is_rejected():
    vertex = make_vertex(0, 0)

    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start_vertex=vertex,
            end_vertex=vertex,
        )


def test_invalid_wall_thickness_is_rejected():
    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start_vertex=make_vertex(0, 0),
            end_vertex=make_vertex(4000, 0),
            thickness=0,
        )


def test_invalid_wall_height_is_rejected():
    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start_vertex=make_vertex(0, 0),
            end_vertex=make_vertex(4000, 0),
            height=-2600,
        )


def test_moving_shared_vertex_changes_wall_length():
    start = make_vertex(0, 0)
    end = make_vertex(4000, 0)

    wall = Wall(
        name="Wall",
        start_vertex=start,
        end_vertex=end,
    )

    end.position = Point2D(5000, 0)

    assert wall.length == 5000