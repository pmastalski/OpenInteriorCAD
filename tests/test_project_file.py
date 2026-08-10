from openinteriorcad.core.project import Project
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D
from openinteriorcad.persistence.project_file import (
    load_project,
    save_project,
)


def create_project():
    project = Project(
        name="Bedroom"
    )

    room = Room(
        name="Bedroom room"
    )

    v1 = Vertex2D(
        position=Point2D(0, 0)
    )

    v2 = Vertex2D(
        position=Point2D(5000, 0)
    )

    room.add_wall(
        Wall(
            name="Wall",
            start_vertex=v1,
            end_vertex=v2,
        )
    )

    project.scene.add(room)

    return project


def test_save_and_load_project(tmp_path):
    project = create_project()

    file_path = (
        tmp_path / "project.oic"
    )

    save_project(
        project,
        file_path,
    )

    loaded = load_project(
        file_path
    )

    assert loaded.id == project.id
    assert loaded.name == project.name

    room = next(
        iter(
            loaded.scene.entities.values()
        )
    )

    assert room.name == "Bedroom room"
    assert room.wall_count == 1
    assert room.walls[0].length == 5000
