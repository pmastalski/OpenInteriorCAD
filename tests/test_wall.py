import pytest

from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


def test_wall_length():
    wall = Wall(
        name="Wall 1",
        start=Point2D(0, 0),
        end=Point2D(4000, 0),
    )

    assert wall.length == 4000


def test_diagonal_wall_length():
    wall = Wall(
        name="Diagonal wall",
        start=Point2D(0, 0),
        end=Point2D(3000, 4000),
    )

    assert wall.length == pytest.approx(5000)


def test_zero_length_wall_is_rejected():
    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start=Point2D(1000, 1000),
            end=Point2D(1000, 1000),
        )


def test_invalid_wall_thickness_is_rejected():
    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start=Point2D(0, 0),
            end=Point2D(4000, 0),
            thickness=0,
        )


def test_invalid_wall_height_is_rejected():
    with pytest.raises(ValueError):
        Wall(
            name="Invalid wall",
            start=Point2D(0, 0),
            end=Point2D(4000, 0),
            height=-2600,
        )