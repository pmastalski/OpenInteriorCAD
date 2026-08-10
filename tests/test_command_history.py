from openinteriorcad.commands.history import CommandHistory
from openinteriorcad.commands.move_vertex import MoveVertexCommand
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.geometry.point2d import Point2D


def test_execute_command_moves_vertex():
    vertex = Vertex2D(
        position=Point2D(0, 0)
    )

    history = CommandHistory()

    command = MoveVertexCommand(
        vertex=vertex,
        new_position=Point2D(1000, 500),
    )

    history.execute(command)

    assert vertex.position == Point2D(1000, 500)


def test_undo_restores_previous_position():
    vertex = Vertex2D(
        position=Point2D(0, 0)
    )

    history = CommandHistory()

    history.execute(
        MoveVertexCommand(
            vertex,
            Point2D(1000, 500),
        )
    )

    history.undo()

    assert vertex.position == Point2D(0, 0)


def test_redo_moves_vertex_again():
    vertex = Vertex2D(
        position=Point2D(0, 0)
    )

    history = CommandHistory()

    history.execute(
        MoveVertexCommand(
            vertex,
            Point2D(1000, 500),
        )
    )

    history.undo()
    history.redo()

    assert vertex.position == Point2D(1000, 500)


def test_new_command_clears_redo_stack():
    vertex = Vertex2D(
        position=Point2D(0, 0)
    )

    history = CommandHistory()

    history.execute(
        MoveVertexCommand(
            vertex,
            Point2D(1000, 0),
        )
    )

    history.undo()

    history.execute(
        MoveVertexCommand(
            vertex,
            Point2D(2000, 0),
        )
    )

    assert history.can_redo is False


def test_undo_empty_history_returns_false():
    history = CommandHistory()

    assert history.undo() is False


def test_redo_empty_history_returns_false():
    history = CommandHistory()

    assert history.redo() is False