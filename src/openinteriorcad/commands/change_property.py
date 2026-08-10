from typing import Any

from openinteriorcad.commands.base import Command


class ChangePropertyCommand(Command):
    """Changes an object's property with undo/redo support."""

    def __init__(
        self,
        target: object,
        property_name: str,
        new_value: Any,
    ) -> None:
        if not hasattr(target, property_name):
            raise AttributeError(
                f"{type(target).__name__} has no property "
                f"'{property_name}'."
            )

        self.target = target
        self.property_name = property_name
        self.new_value = new_value
        self.old_value = getattr(
            target,
            property_name,
        )

    def execute(self) -> None:
        setattr(
            self.target,
            self.property_name,
            self.new_value,
        )

    def undo(self) -> None:
        setattr(
            self.target,
            self.property_name,
            self.old_value,
        )