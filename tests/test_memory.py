"""Tests for the memory module."""
import pytest
from datetime import datetime
from src.memory.memory import Memory, ToolMemory, ConversationMemory

@pytest.fixture
def memory():
    """Create a memory instance for testing."""
    return Memory(max_history=5)

def test_add_tool_memory(memory):
    """Test adding tool execution to memory."""
    tool_memory = memory.add_tool_memory(
        tool_name="search",
        input_data={"query": "test"},
        output_data=["result1", "result2"]
    )
    
    assert isinstance(tool_memory, ToolMemory)
    assert tool_memory.tool_name == "search"
    assert tool_memory.input_data == {"query": "test"}
    assert tool_memory.output_data == ["result1", "result2"]
    assert isinstance(tool_memory.timestamp, datetime)
    assert len(memory.tool_history) == 1

def test_add_conversation_memory(memory):
    """Test adding conversation to memory."""
    # Add a tool memory first
    tool_memory = memory.add_tool_memory(
        tool_name="search",
        input_data={"query": "test"},
        output_data=["result1", "result2"]
    )
    
    # Add conversation with tool output
    memory.add_conversation_memory(
        role="user",
        content="Search for test",
        related_tool_outputs=[tool_memory]
    )
    
    assert len(memory.conversation_history) == 1
    entry = memory.conversation_history[0]
    assert isinstance(entry, ConversationMemory)
    assert entry.role == "user"
    assert entry.content == "Search for test"
    assert len(entry.related_tool_outputs) == 1
    assert entry.related_tool_outputs[0] == tool_memory

def test_get_conversation_context(memory):
    """Test getting formatted conversation context."""
    # Add some conversation history with tool outputs
    tool_memory = memory.add_tool_memory(
        tool_name="search",
        input_data={"query": "test"},
        output_data=["result1", "result2"]
    )
    
    memory.add_conversation_memory(
        role="user",
        content="Search for test",
        related_tool_outputs=[tool_memory]
    )
    
    memory.add_conversation_memory(
        role="assistant",
        content="Here are the results",
        related_tool_outputs=[]
    )
    
    context = memory.get_conversation_context()
    assert "user: Search for test" in context
    assert "assistant: Here are the results" in context
    assert "[Tool Output - search]" in context
    assert "Input: {'query': 'test'}" in context
    assert "Output: ['result1', 'result2']" in context

def test_max_history_limit(memory):
    """Test that history is trimmed to max_history."""
    # Add more entries than max_history
    for i in range(10):
        memory.add_tool_memory(
            tool_name=f"tool{i}",
            input_data={"id": i},
            output_data=f"result{i}"
        )
        memory.add_conversation_memory(
            role="user",
            content=f"message{i}"
        )
    
    # Check that history is trimmed
    assert len(memory.tool_history) == 5
    assert len(memory.conversation_history) == 5
    
    # Verify we kept the most recent entries
    assert memory.tool_history[-1].tool_name == "tool9"
    assert memory.conversation_history[-1].content == "message9"

def test_get_relevant_tool_outputs(memory):
    """Test getting relevant tool outputs."""
    # Add some tool outputs
    for i in range(3):
        memory.add_tool_memory(
            tool_name=f"tool{i}",
            input_data={"id": i},
            output_data=f"result{i}"
        )
    
    # Get relevant outputs
    outputs = memory.get_relevant_tool_outputs("test query", max_results=2)
    assert len(outputs) == 2
    assert outputs[-1].tool_name == "tool2"  # Most recent
    assert outputs[-2].tool_name == "tool1"  # Second most recent 