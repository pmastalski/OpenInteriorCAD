import pytest

from openinteriorcad.commands.change_property import (
    ChangePropertyCommand,
)
from openinteriorcad.commands.history import CommandHistory
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


def create_wall():
    return Wall(
        name="Wall 1",
        start_vertex=Vertex2D(
            position=Point2D(0, 0)
        ),
        end_vertex=Vertex2D(
            position=Point2D(4000, 0)
        ),
        thickness=120,
        height=2600,
    )


def test_change_wall_height():
    wall = create_wall()
    history = CommandHistory()

    history.execute(
        ChangePropertyCommand(
            wall,
            "height",
            2800,
        )
    )

    assert wall.height == 2800


def test_undo_property_change():
    wall = create_wall()
    history = CommandHistory()

    history.execute(
        ChangePropertyCommand(
            wall,
            "thickness",
            180,
        )
    )

    history.undo()

    assert wall.thickness == 120


def test_redo_property_change():
    wall = create_wall()
    history = CommandHistory()

    history.execute(
        ChangePropertyCommand(
            wall,
            "height",
            3000,
        )
    )

    history.undo()
    history.redo()

    assert wall.height == 3000


def test_change_entity_name():
    wall = create_wall()
    history = CommandHistory()

    history.execute(
        ChangePropertyCommand(
            wall,
            "name",
            "North wall",
        )
    )

    assert wall.name == "North wall"


def test_unknown_property_is_rejected():
    wall = create_wall()

    with pytest.raises(AttributeError):
        ChangePropertyCommand(
            wall,
            "banana",
            123,
        )