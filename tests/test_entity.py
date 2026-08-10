import pytest

from openinteriorcad.core.entity import Entity


def test_entity_has_unique_id():
    first = Entity(name="Wall 1")
    second = Entity(name="Wall 2")

    assert first.id != second.id


def test_entity_name():
    entity = Entity(name="Kitchen")

    assert entity.name == "Kitchen"


def test_entity_cannot_have_empty_name():
    with pytest.raises(ValueError):
        Entity(name="   ")