from typing import Dict, Any
from langchain_core.callbacks import BaseCallbackHandler
from src.config.logging_config import get_logger

class ToolUsageCallback(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.logger = get_logger('console')
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        tool_name = serialized.get("name", "unknown")
        self.logger.info(f"\n> Using tool: {tool_name}")
        self.logger.info(f"> Input: {input_str}\n")
    
    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        self.logger.info(f"> Tool output received\n") 