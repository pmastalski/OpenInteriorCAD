from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.geometry.point2d import Point2D


def test_vertex_has_unique_id():
    first = Vertex2D(
        position=Point2D(0, 0)
    )

    second = Vertex2D(
        position=Point2D(0, 0)
    )

    assert first.id != second.id


def test_vertex_position_can_change():
    vertex = Vertex2D(
        position=Point2D(0, 0)
    )

    vertex.position = Point2D(1000, 500)

    assert vertex.position == Point2D(1000, 500)