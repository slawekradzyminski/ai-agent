"""Handler for HTTP request commands."""
import json
import logging
from typing import Any, Dict

from src.cli.handlers.base import BaseHandler

logger = logging.getLogger(__name__)

class HttpHandler(BaseHandler):
    """Handler for http: commands."""
    
    def can_handle(self, command: str) -> bool:
        """Check if the command is an HTTP command."""
        return command.lower().startswith('http:')
    
    async def handle(self, command: str) -> Dict[str, Any]:
        """Process the HTTP command and return result."""
        url = command[5:].strip()
        logger.info(f"Processing http request: {url}")
        return await self.agent.http_request(url)
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format HTTP result for display."""
        if 'error' in result:
            return f"\nError: {result['error']}"
        
        return "\nJSON Response:\n" + "-" * 50 + "\n" + json.dumps(result, indent=2) 