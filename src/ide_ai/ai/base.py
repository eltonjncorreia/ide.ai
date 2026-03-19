from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class AIProvider(ABC):
    """Common interface for all AI CLI providers."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def send(self, message: str, context: list[str] = []) -> AsyncIterator[str]: ...

    @abstractmethod
    async def clear_session(self) -> None: ...
