from openinteriorcad.core.project import Project
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D
from openinteriorcad.persistence.serializer import (
    project_from_dict,
    project_to_dict,
)


def create_project():
    project = Project(
        name="Kitchen"
    )

    room = Room(
        name="Main room"
    )

    v1 = Vertex2D(
        position=Point2D(0, 0)
    )

    v2 = Vertex2D(
        position=Point2D(4000, 0)
    )

    v3 = Vertex2D(
        position=Point2D(4000, 3000)
    )

    room.add_wall(
        Wall(
            name="Wall 1",
            start_vertex=v1,
            end_vertex=v2,
        )
    )

    room.add_wall(
        Wall(
            name="Wall 2",
            start_vertex=v2,
            end_vertex=v3,
        )
    )

    project.scene.add(room)

    return project


def test_project_serialization_preserves_name():
    project = create_project()

    data = project_to_dict(project)

    loaded = project_from_dict(data)

    assert loaded.name == project.name


def test_project_serialization_preserves_id():
    project = create_project()

    data = project_to_dict(project)

    loaded = project_from_dict(data)

    assert loaded.id == project.id


def test_room_serialization_preserves_id():
    project = create_project()

    original_room = next(
        iter(project.scene.entities.values())
    )

    data = project_to_dict(project)

    loaded = project_from_dict(data)

    loaded_room = next(
        iter(loaded.scene.entities.values())
    )

    assert loaded_room.id == original_room.id


def test_shared_vertex_is_preserved():
    project = create_project()

    data = project_to_dict(project)

    loaded = project_from_dict(data)

    room = next(
        iter(loaded.scene.entities.values())
    )

    wall_1 = room.walls[0]
    wall_2 = room.walls[1]

    assert (
        wall_1.end_vertex
        is wall_2.start_vertex
    )