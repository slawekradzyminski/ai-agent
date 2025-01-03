"""Search command handler."""
import logging
from typing import List, Dict, Any
from .base import BaseHandler

logger = logging.getLogger(__name__)

class SearchHandler(BaseHandler):
    """Handler for search commands."""

    def can_handle(self, message: str) -> bool:
        """Check if this handler can process the message."""
        return message.lower().startswith("search:")

    async def handle(self, message: str) -> List[Dict[str, Any]]:
        """
        Process a search command.

        Args:
            message: The search command message

        Returns:
            List of search results
        """
        # Extract query
        query = message.replace("search:", "", 1).strip()
        logger.info(f"Processing search request: {query}")
        
        try:
            return await self.agent.search(query)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return [{"error": f"Search failed: {str(e)}"}]

    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for display.

        Args:
            results: List of search results to format

        Returns:
            Formatted string for display
        """
        if not results:
            return "No results found"
            
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
            
        output = []
        for result in results:
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            output.append(f"Title: {title}")
            output.append(f"Link: {link}")
            output.append("")
            
        return "\n".join(output) 