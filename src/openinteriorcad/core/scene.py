from dataclasses import dataclass, field
from uuid import UUID

from .entity import Entity


@dataclass
class Scene:
    """Container for entities belonging to a project."""

    entities: dict[UUID, Entity] = field(default_factory=dict)

    def add(self, entity: Entity) -> None:
        if entity.id in self.entities:
            raise ValueError(
                f"Entity {entity.id} already exists in the scene."
            )

        self.entities[entity.id] = entity

    def remove(self, entity_id: UUID) -> Entity:
        if entity_id not in self.entities:
            raise KeyError(
                f"Entity {entity_id} does not exist."
            )

        return self.entities.pop(entity_id)

    def get(self, entity_id: UUID) -> Entity | None:
        return self.entities.get(entity_id)

    def clear(self) -> None:
        self.entities.clear()

    def __len__(self) -> int:
        return len(self.entities)