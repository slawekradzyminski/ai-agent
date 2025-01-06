from langchain_core.callbacks import BaseCallbackHandler
from typing import Any
from src.memory.vector_memory import VectorMemory

class ToolOutputCallbackHandler(BaseCallbackHandler):
    def __init__(self, memory: VectorMemory):
        super().__init__()
        self.memory = memory
    
    async def on_tool_end(
        self,
        output: str,
        *,
        tool_name: str = None,
        tool_input: str = None,
        **kwargs: Any
    ) -> None:
        """Store tool output in memory when tool execution ends."""
        if tool_name is None or tool_input is None:
            return
        self.memory.add_tool_memory(tool_name, str(tool_input), str(output)) 