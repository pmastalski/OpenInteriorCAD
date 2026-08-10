from openinteriorcad.commands.base import Command
from openinteriorcad.core.entity import Entity
from openinteriorcad.core.scene import Scene


class AddEntityCommand(Command):
    """Adds an entity to a scene."""

    def __init__(
        self,
        scene: Scene,
        entity: Entity,
    ) -> None:
        self.scene = scene
        self.entity = entity

    def execute(self) -> None:
        self.scene.add(self.entity)

    def undo(self) -> None:
        self.scene.remove(self.entity.id)