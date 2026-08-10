import pytest

from openinteriorcad.geometry.point2d import Point2D


def test_distance_horizontal():
    first = Point2D(0, 0)
    second = Point2D(4000, 0)

    assert first.distance_to(second) == 4000


def test_distance_vertical():
    first = Point2D(0, 0)
    second = Point2D(0, 2500)

    assert first.distance_to(second) == 2500


def test_distance_diagonal():
    first = Point2D(0, 0)
    second = Point2D(3000, 4000)

    assert first.distance_to(second) == pytest.approx(5000)