"""Memory module for storing conversation and tool outputs."""
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.memory import BaseMemory

logger = logging.getLogger(__name__)

class ToolMemory(BaseModel):
    """Memory for tool outputs."""
    tool_name: str
    input: str
    output: str

class Memory(BaseMemory):
    """Memory for storing conversation history and tool outputs."""
    
    messages: List[BaseMessage] = Field(default_factory=list)
    tool_outputs: List[ToolMemory] = Field(default_factory=list)
    max_history: int = Field(default=10)
    
    @property
    def memory_variables(self) -> List[str]:
        """Return the memory variables."""
        return ["chat_history", "tool_history"]
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to memory."""
        self.messages.append(HumanMessage(content=message))
        self._trim_history()

    def add_ai_message(self, message: str) -> None:
        """Add an AI message to memory."""
        self.messages.append(AIMessage(content=message))
        self._trim_history()

    def add_tool_memory(self, tool_name: str, input: str, output: str) -> None:
        """Add a tool output to memory."""
        self.tool_outputs.append(
            ToolMemory(tool_name=tool_name, input=input, output=output)
        )

    def get_conversation_context(self) -> List[BaseMessage]:
        """Get the conversation context."""
        return self.messages[-self.max_history:]

    def get_relevant_tool_outputs(self, query: str) -> List[Dict[str, Any]]:
        """Get tool outputs relevant to the query."""
        # For now, return all tool outputs in a format matching the tests
        return [
            {
                "tool": memory.tool_name,
                "input": memory.input,
                "output": memory.output
            }
            for memory in self.tool_outputs
        ]

    def _trim_history(self) -> None:
        """Trim history to max_history messages."""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables."""
        tool_outputs = self.get_relevant_tool_outputs(inputs.get("input", ""))
        tool_messages = []
        for output in tool_outputs:
            content = (
                f"Previous tool usage - {output['tool']}:\n"
                f"Input: {output['input']}\n"
                f"Output: {output['output']}"
            )
            tool_messages.append(SystemMessage(content=content))
            
        return {
            "chat_history": self.get_conversation_context(),
            "tool_history": tool_messages
        }

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        if "input" in inputs:
            self.add_user_message(inputs["input"])
        if "output" in outputs:
            self.add_ai_message(outputs["output"])

    def clear(self) -> None:
        """Clear memory contents."""
        self.messages.clear()
        self.tool_outputs.clear() 