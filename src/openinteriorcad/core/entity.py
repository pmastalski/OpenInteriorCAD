from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    """Base class for all OpenInteriorCAD project entities."""

    name: str = "Entity"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Entity name cannot be empty.")