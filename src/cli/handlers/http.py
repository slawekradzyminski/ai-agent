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
        
        # Handle both old and new response formats
        if 'status_code' in result:
            # New format with detailed response info
            output = [
                f"\nStatus Code: {result['status_code']}",
                f"Content Type: {result['content_type']}",
                "-" * 50
            ]
            
            data = result['data']
            if isinstance(data, dict) and 'content_type' in data:
                # Text/HTML/Other content
                output.append(data['content'])
            else:
                # JSON content
                output.append(json.dumps(data, indent=2))
        else:
            # Old format or simple response
            output = [
                "\nJSON Response",
                "-" * 50,
                json.dumps(result, indent=2)
            ]
            
        return "\n".join(output) 