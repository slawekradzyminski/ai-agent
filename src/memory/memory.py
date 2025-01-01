"""Memory module for storing conversation history and tool outputs."""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ToolMemory:
    """Memory entry for tool execution."""
    tool_name: str
    input_data: Dict[str, Any]
    output_data: Any
    timestamp: datetime

@dataclass
class ConversationMemory:
    """Memory entry for conversation."""
    role: str
    content: str
    timestamp: datetime
    related_tool_outputs: List[ToolMemory]

class Memory:
    """Memory management for the agent."""

    def __init__(self, max_history: int = 100):
        """Initialize memory with maximum history size."""
        self.max_history = max_history
        self.conversation_history: List[ConversationMemory] = []
        self.tool_history: List[ToolMemory] = []

    def add_tool_memory(self, tool_name: str, input_data: Dict[str, Any], output_data: Any) -> ToolMemory:
        """
        Add a tool execution to memory.

        Args:
            tool_name: Name of the tool used
            input_data: Input parameters for the tool
            output_data: Output from the tool execution

        Returns:
            The created ToolMemory entry
        """
        memory = ToolMemory(
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            timestamp=datetime.now()
        )
        self.tool_history.append(memory)
        
        # Trim history if needed
        if len(self.tool_history) > self.max_history:
            self.tool_history = self.tool_history[-self.max_history:]
        
        return memory

    def add_conversation_memory(
        self,
        role: str,
        content: str,
        related_tool_outputs: Optional[List[ToolMemory]] = None
    ) -> None:
        """
        Add a conversation entry to memory.

        Args:
            role: Role of the speaker (user/assistant)
            content: Content of the message
            related_tool_outputs: Optional list of related tool outputs
        """
        memory = ConversationMemory(
            role=role,
            content=content,
            timestamp=datetime.now(),
            related_tool_outputs=related_tool_outputs or []
        )
        self.conversation_history.append(memory)
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_conversation_context(self, max_entries: Optional[int] = None) -> str:
        """
        Get formatted conversation history for context.

        Args:
            max_entries: Optional maximum number of entries to include

        Returns:
            Formatted conversation history with tool outputs
        """
        history = self.conversation_history[-max_entries:] if max_entries else self.conversation_history
        context_parts = []

        for entry in history:
            # Add the conversation message
            context_parts.append(f"{entry.role}: {entry.content}")
            
            # Add any related tool outputs
            for tool in entry.related_tool_outputs:
                context_parts.append(
                    f"[Tool Output - {tool.tool_name}]\n"
                    f"Input: {tool.input_data}\n"
                    f"Output: {tool.output_data}"
                )
        
        return "\n\n".join(context_parts)

    def get_relevant_tool_outputs(self, query: str, max_results: int = 5) -> List[ToolMemory]:
        """
        Get tool outputs relevant to a query.

        Args:
            query: The query to match against
            max_results: Maximum number of results to return

        Returns:
            List of relevant tool outputs
        """
        # For now, return the most recent tool outputs
        # TODO: Implement semantic search for better relevance
        return self.tool_history[-max_results:] 