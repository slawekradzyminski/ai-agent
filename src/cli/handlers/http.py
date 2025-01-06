import json
import logging
from typing import Dict, Any, Union
from src.cli.handlers.base import BaseHandler

logger = logging.getLogger(__name__)

class HttpHandler(BaseHandler):
    def can_handle(self, command: str) -> bool:
        command = command.lower()
        return command.startswith("http ") or command.startswith("http:")
    
    async def handle(self, command: str) -> Dict[str, Any]:
        if ":" in command:
            url = command.split(":", 1)[1].strip()
        else:
            url = command[len("http "):].strip()
            
        if not url:
            logger.warning("Empty URL provided")
            return self.get_help()
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url.lstrip('/')
            
        logger.info(f"Making HTTP request to URL: {url}")
        result = await self.agent.make_http_request(url)
        logger.info("Got response from agent")
        return result
        
    def format_result(self, result: Union[Dict[str, Any], str]) -> str:
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
                return "\nJSON Response\n" + "-" * 50 + "\n" + json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                return "\nText Response\n" + "-" * 50 + "\n" + result
                
        if isinstance(result, dict) and 'error' in result:
            return f"\nError: {result['error']}"
        
        if isinstance(result, dict) and 'status_code' in result:
            output = [
                f"\nStatus Code: {result['status_code']}",
                f"Content Type: {result['content_type']}",
                "-" * 50
            ]
            
            data = result['data']
            if isinstance(data, dict) and 'content_type' in data:
                output.append(data['content'])
            else:
                output.append(json.dumps(data, indent=2))
        else:
            output = [
                "\nJSON Response",
                "-" * 50,
                json.dumps(result, indent=2)
            ]
            
        return "\n".join(output)
        
    def get_help(self) -> str:
        return "- http <url>: Make an HTTP request to a URL" 