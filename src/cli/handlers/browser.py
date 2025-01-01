"""Handler for browser commands."""
import logging
from typing import Any

from src.cli.handlers.base import BaseHandler

logger = logging.getLogger(__name__)

class BrowserHandler(BaseHandler):
    """Handler for browser: commands."""
    
    def can_handle(self, command: str) -> bool:
        """Check if the command is a browser command."""
        return command.lower().startswith('browser:')
    
    async def handle(self, command: str) -> str:
        """Process the browser command and return content."""
        url = command[8:].strip()
        logger.info(f"Processing browser request: {url}")
        return await self.agent.get_page_content(url)
    
    def format_result(self, url: str, content: str) -> str:
        """Format browser result for display."""
        preview_length = min(500, len(content))
        preview = content[:preview_length] + ("..." if len(content) > preview_length else "")
        
        return f"\nPage Content from {url}:\n" + "-" * 50 + f"\n{preview}" 