from abc import ABC, abstractmethod


class Command(ABC):
    """Base interface for all reversible user actions."""

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        raise NotImplementedError

    def redo(self) -> None:
        self.execute()