from openinteriorcad.commands.add_entity import AddEntityCommand
from openinteriorcad.commands.history import CommandHistory
from openinteriorcad.commands.remove_entity import RemoveEntityCommand
from openinteriorcad.core.entity import Entity
from openinteriorcad.core.scene import Scene


def test_add_entity_command():
    scene = Scene()
    entity = Entity(name="Test entity")

    history = CommandHistory()

    history.execute(
        AddEntityCommand(
            scene,
            entity,
        )
    )

    assert scene.get(entity.id) is entity


def test_undo_add_entity():
    scene = Scene()
    entity = Entity(name="Test entity")

    history = CommandHistory()

    history.execute(
        AddEntityCommand(
            scene,
            entity,
        )
    )

    history.undo()

    assert scene.get(entity.id) is None


def test_redo_add_entity():
    scene = Scene()
    entity = Entity(name="Test entity")

    history = CommandHistory()

    history.execute(
        AddEntityCommand(
            scene,
            entity,
        )
    )

    history.undo()
    history.redo()

    assert scene.get(entity.id) is entity


def test_remove_entity_command():
    scene = Scene()
    entity = Entity(name="Test entity")

    scene.add(entity)

    history = CommandHistory()

    history.execute(
        RemoveEntityCommand(
            scene,
            entity.id,
        )
    )

    assert scene.get(entity.id) is None


def test_undo_remove_entity():
    scene = Scene()
    entity = Entity(name="Test entity")

    scene.add(entity)

    history = CommandHistory()

    history.execute(
        RemoveEntityCommand(
            scene,
            entity.id,
        )
    )

    history.undo()

    assert scene.get(entity.id) is entity