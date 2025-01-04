"""Browser command handler."""
import logging
from typing import Dict, Any
from .base import BaseHandler

logger = logging.getLogger(__name__)

class BrowserHandler(BaseHandler):
    """Handler for browser commands."""

    def can_handle(self, command: str) -> bool:
        """Check if this handler can process the given command."""
        command = command.lower()
        return command.startswith("browser ") or command.startswith("browser:")

    async def handle(self, command: str) -> Dict[str, Any]:
        """Process the browser command and return the result."""
        # Extract URL after "browser:" or "browser "
        if ":" in command:
            url = command.split(":", 1)[1].strip()
        else:
            url = command[len("browser "):].strip()
            
        if not url:
            return self.get_help()
            
        return await self.agent.get_page_content(url)
        
    def format_result(self, result: str) -> str:
        """Format browser result for display."""
        if not result:
            return "No content retrieved"
            
        if result.startswith("Error:"):
            return result
            
        # Truncate long content
        max_length = 500
        if len(result) > max_length:
            return result[:max_length] + "..."
            
        return result
        
    def get_help(self) -> str:
        """Get help text for browser commands."""
        return "- browser <url>: Browse a webpage and extract its content" 