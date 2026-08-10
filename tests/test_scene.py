import pytest

from openinteriorcad.core.entity import Entity
from openinteriorcad.core.scene import Scene


def test_add_entity_to_scene():
    scene = Scene()
    entity = Entity(name="Wall")

    scene.add(entity)

    assert len(scene) == 1
    assert scene.get(entity.id) is entity


def test_remove_entity_from_scene():
    scene = Scene()
    entity = Entity(name="Wall")

    scene.add(entity)
    removed = scene.remove(entity.id)

    assert removed is entity
    assert len(scene) == 0


def test_duplicate_entity_is_rejected():
    scene = Scene()
    entity = Entity(name="Wall")

    scene.add(entity)

    with pytest.raises(ValueError):
        scene.add(entity)