import logging
from typing import Dict, Any
from .base import BaseHandler

logger = logging.getLogger(__name__)

class BrowserHandler(BaseHandler):
    def can_handle(self, command: str) -> bool:
        command = command.lower()
        return command.startswith("browser ") or command.startswith("browser:")

    async def handle(self, command: str) -> Dict[str, Any]:
        if ":" in command:
            url = command.split(":", 1)[1].strip()
        else:
            url = command[len("browser "):].strip()
            
        if not url:
            logger.warning("Empty URL provided")
            return {"error": "URL is required"}
            
        logger.info(f"Making browser request to URL: {url}")
        result = await self.agent.get_page_content(url)
        logger.info("Got response from agent")
        return result
        
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No content retrieved"
            
        if "error" in result:
            return f"\nError: {result['error']}"
            
        if "content" not in result:
            return f"\nError: Invalid response format"
            
        content = result["content"]
        if not content:
            return "No content retrieved"
            
        formatted = f"\nContent from {result.get('url', 'unknown URL')}:\n" + "-" * 50 + "\n" + content
        
        max_length = 1000
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "..."
            
        return formatted
        
    def get_help(self) -> str:
        return "- browser <url>: Browse a webpage and extract its content" 