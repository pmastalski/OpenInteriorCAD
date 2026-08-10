import pytest

from openinteriorcad.core.project import Project


def test_create_project():
    project = Project(name="Kitchen Project")

    assert project.name == "Kitchen Project"
    assert len(project.scene) == 0


def test_project_cannot_have_empty_name():
    with pytest.raises(ValueError):
        Project(name="")