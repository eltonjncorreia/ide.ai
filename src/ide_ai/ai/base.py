from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class AIProvider(ABC):
    """Common interface for all AI CLI providers.
    
    Each provider instance is independent and thread-safe. Multiple instances
    can run concurrent requests without blocking each other. The send() method
    is fully async and yields chunks as they arrive from the subprocess.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name (e.g., 'Claude', 'Copilot')."""
        ...

    @abstractmethod
    async def send(self, message: str, context: list[str] = []) -> AsyncIterator[str]:
        """Send a message and stream the response.
        
        This method is async and yields response chunks as they arrive.
        Multiple concurrent calls to send() on different instances do not
        block each other - each runs independently.
        
        Args:
            message: The user message to send
            context: Optional list of context strings (files, etc.) to prepend
            
        Yields:
            Response chunks as they arrive from the AI provider
        """
        ...

    @abstractmethod
    async def clear_session(self) -> None:
        """Clear any session state for this provider instance."""
        ...
