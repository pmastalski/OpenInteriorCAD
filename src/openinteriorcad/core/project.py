from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .scene import Scene


@dataclass
class Project:
    """Root object representing an OpenInteriorCAD project."""

    name: str = "Untitled Project"
    id: UUID = field(default_factory=uuid4)
    scene: Scene = field(default_factory=Scene)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Project name cannot be empty.")