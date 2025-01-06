import logging
from typing import List, Dict, Any
from .base import BaseHandler

logger = logging.getLogger(__name__)

class SearchHandler(BaseHandler):
    def can_handle(self, command: str) -> bool:
        command = command.lower()
        return command.startswith("search ") or command.startswith("search:")

    async def handle(self, command: str) -> List[Dict[str, Any]]:
        if ":" in command:
            query = command.split(":", 1)[1].strip()
        else:
            query = command[len("search "):].strip()
            
        if not query:
            return self.get_help()
            
        return await self.agent.search(query)
        
    def format_results(self, results: List[Dict[str, Any]]) -> str:
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
        return "- search <query>: Search the web for information" 