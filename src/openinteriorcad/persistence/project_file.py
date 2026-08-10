import json
from pathlib import Path

from openinteriorcad.core.project import Project
from openinteriorcad.persistence.serializer import (
    project_from_dict,
    project_to_dict,
)


def save_project(
    project: Project,
    path: str | Path,
) -> None:
    path = Path(path)

    data = project_to_dict(project)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_project(
    path: str | Path,
) -> Project:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    return project_from_dict(data)