"""Search command handler."""
import logging
from typing import List, Dict, Any
from .base import BaseHandler

logger = logging.getLogger(__name__)

class SearchHandler(BaseHandler):
    """Handler for search commands."""

    def can_handle(self, command: str) -> bool:
        """Check if this handler can process the given command."""
        command = command.lower()
        return command.startswith("search ") or command.startswith("search:")

    async def handle(self, command: str) -> List[Dict[str, Any]]:
        """Process the search command and return the result."""
        # Extract query after "search:" or "search "
        if ":" in command:
            query = command.split(":", 1)[1].strip()
        else:
            query = command[len("search "):].strip()
            
        if not query:
            return self.get_help()
            
        return await self.agent.search(query)
        
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        if not results:
            return "No results found"
            
        if isinstance(results, list) and len(results) > 0 and "error" in results[0]:
            return f"Error: {results[0]['error']}"
            
        output = []
        for result in results:
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            output.append(f"Title: {title}")
            output.append(f"Link: {link}")
            output.append("")
            
        return "\n".join(output)
        
    def get_help(self) -> str:
        """Get help text for search commands."""
        return "- search <query>: Search the web for information" 