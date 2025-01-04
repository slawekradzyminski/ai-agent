"""Base handler for CLI commands."""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseHandler(ABC):
    """Base class for all command handlers."""
    
    def __init__(self, agent):
        """Initialize the handler with an agent instance."""
        self.agent = agent
    
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check if this handler can process the given command."""
        pass
    
    @abstractmethod
    async def handle(self, command: str) -> Any:
        """Process the command and return the result."""
        pass
        
    @abstractmethod
    def get_help(self) -> str:
        """Get help text for this handler's commands."""
        pass 