from openinteriorcad.commands.base import Command
from openinteriorcad.core.entity import Entity
from openinteriorcad.core.scene import Scene


class RemoveEntityCommand(Command):
    """Removes an entity from a scene."""

    def __init__(
        self,
        scene: Scene,
        entity_id,
    ) -> None:
        self.scene = scene
        self.entity_id = entity_id
        self._removed_entity: Entity | None = None

    def execute(self) -> None:
        self._removed_entity = self.scene.remove(
            self.entity_id
        )

    def undo(self) -> None:
        if self._removed_entity is None:
            raise RuntimeError(
                "Cannot undo before command execution."
            )

        self.scene.add(
            self._removed_entity
        )