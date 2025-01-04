"""HTTP command handler."""
import json
from typing import Dict, Any
from src.cli.handlers.base import BaseHandler

class HttpHandler(BaseHandler):
    """Handler for HTTP commands."""
    
    def can_handle(self, command: str) -> bool:
        """Check if this handler can process the given command."""
        command = command.lower()
        return command.startswith("http ") or command.startswith("http:")
    
    async def handle(self, command: str) -> Dict[str, Any]:
        """Process the HTTP command and return the result."""
        # Extract URL after "http:" or "http "
        if ":" in command:
            url = command.split(":", 1)[1].strip()
        else:
            url = command[len("http "):].strip()
            
        if not url:
            return self.get_help()
            
        return await self.agent.make_http_request(url)
        
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
        
    def get_help(self) -> str:
        """Get help text for HTTP commands."""
        return "- http <url>: Make an HTTP request to a URL" 