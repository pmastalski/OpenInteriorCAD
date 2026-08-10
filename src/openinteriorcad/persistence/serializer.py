from uuid import UUID

from openinteriorcad.core.project import Project
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D

FORMAT_NAME = "OpenInteriorCAD"
FORMAT_VERSION = "0.1"


def project_to_dict(project: Project) -> dict:
    entities = []

    for entity in project.scene.entities.values():

        if isinstance(entity, Room):
            entities.append(
                {
                    "type": "Room",
                    "id": str(entity.id),
                    "name": entity.name,
                    "vertices": [
                        {
                            "id": str(vertex.id),
                            "x": vertex.position.x,
                            "y": vertex.position.y,
                        }
                        for vertex in entity.vertices
                    ],
                    "walls": [
                        {
                            "id": str(wall.id),
                            "name": wall.name,
                            "start_vertex_id": str(
                                wall.start_vertex.id
                            ),
                            "end_vertex_id": str(
                                wall.end_vertex.id
                            ),
                            "thickness": wall.thickness,
                            "height": wall.height,
                        }
                        for wall in entity.walls
                    ],
                }
            )

    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "project": {
            "id": str(project.id),
            "name": project.name,
        },
        "entities": entities,
    }


def project_from_dict(data: dict) -> Project:
    if data.get("format") != FORMAT_NAME:
        raise ValueError("Invalid project format.")

    if data.get("version") != FORMAT_VERSION:
        raise ValueError("Unsupported project version.")

    project_data = data["project"]

    project = Project(
        name=project_data["name"],
        id=UUID(project_data["id"]),
    )

    for entity_data in data.get("entities", []):

        if entity_data["type"] != "Room":
            continue

        room = Room(
            name=entity_data["name"],
            id=UUID(entity_data["id"]),
        )

        vertices_by_id = {}

        for vertex_data in entity_data["vertices"]:
            vertex = Vertex2D(
                id=UUID(vertex_data["id"]),
                position=Point2D(
                    vertex_data["x"],
                    vertex_data["y"],
                ),
            )

            vertices_by_id[vertex.id] = vertex
            room.add_vertex(vertex)

        for wall_data in entity_data["walls"]:
            start_id = UUID(
                wall_data["start_vertex_id"]
            )

            end_id = UUID(
                wall_data["end_vertex_id"]
            )

            wall = Wall(
                id=UUID(wall_data["id"]),
                name=wall_data["name"],
                start_vertex=vertices_by_id[start_id],
                end_vertex=vertices_by_id[end_id],
                thickness=wall_data["thickness"],
                height=wall_data["height"],
            )

            room.add_wall(wall)

        project.scene.add(room)

    return project