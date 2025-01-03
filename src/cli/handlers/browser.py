"""Browser command handler."""
import logging
from .base import BaseHandler

logger = logging.getLogger(__name__)

class BrowserHandler(BaseHandler):
    """Handler for browser commands."""

    def can_handle(self, message: str) -> bool:
        """Check if this handler can process the message."""
        return message.lower().startswith("browser:")

    async def handle(self, message: str) -> str:
        """
        Process a browser command.

        Args:
            message: The browser command message

        Returns:
            The page content or error message
        """
        # Extract URL
        url = message.replace("browser:", "", 1).strip()
        logger.info(f"Processing browser request: {url}")
        
        try:
            return await self.agent.get_page_content(url)
        except Exception as e:
            logger.error(f"Browser request failed: {str(e)}")
            return f"Error: Browser request failed: {str(e)}"

    def format_result(self, result: str) -> str:
        """
        Format browser result for display.

        Args:
            result: The result to format

        Returns:
            Formatted string for display
        """
        if not result:
            return "No content retrieved"
            
        if result.startswith("Error:"):
            return result
            
        # Truncate long content
        max_length = 500
        if len(result) > max_length:
            return result[:max_length] + "..."
            
        return result 