"""Handler for search commands."""
import logging
from typing import Any, Dict, List

from src.cli.handlers.base import BaseHandler

logger = logging.getLogger(__name__)

class SearchHandler(BaseHandler):
    """Handler for search: commands."""
    
    def can_handle(self, command: str) -> bool:
        """Check if the command is a search command."""
        return command.lower().startswith('search:')
    
    async def handle(self, command: str) -> List[Dict[str, Any]]:
        """Process the search command and return results."""
        query = command[7:].strip()
        logger.info(f"Processing search request: {query}")
        return await self.agent.search(query)

    def format_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        output = [f"\nSearch Results for: {query}", "-" * (len(query) + 20)]
        
        if not results:
            logger.warning("No search results found")
            output.append("No results found.")
            return "\n".join(output)
        
        for i, result in enumerate(results, 1):
            try:
                output.extend([
                    f"\n{i}. {result.get('title', 'No title')}",
                    f"   {result.get('link', 'No link')}",
                ])
                if 'snippet' in result:
                    output.append(f"   {result['snippet']}")
                output.append(f"   Source: {result.get('source', 'unknown')}")
            except Exception as e:
                logger.error(f"Error displaying result {i}: {str(e)}")
                continue
        
        return "\n".join(output) 