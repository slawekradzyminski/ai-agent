"""Test memory module."""
import pytest
from unittest.mock import Mock
from src.memory.memory import Memory, ToolMemory
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def memory():
    """Create a memory instance for testing."""
    return Memory()

def test_add_tool_memory(memory):
    """Test adding tool memory."""
    memory.add_tool_memory("test_tool", "test input", "test output")
    assert len(memory.tool_outputs) == 1
    assert memory.tool_outputs[0].tool_name == "test_tool"
    assert memory.tool_outputs[0].input == "test input"
    assert memory.tool_outputs[0].output == "test output"

def test_add_conversation_memory(memory):
    """Test adding conversation memory."""
    memory.add_user_message("test user message")
    memory.add_ai_message("test ai message")
    
    assert len(memory.messages) == 2
    assert isinstance(memory.messages[0], HumanMessage)
    assert isinstance(memory.messages[1], AIMessage)
    assert memory.messages[0].content == "test user message"
    assert memory.messages[1].content == "test ai message"

def test_get_conversation_context(memory):
    """Test getting conversation context."""
    memory.add_user_message("test user message")
    memory.add_ai_message("test ai message")
    
    context = memory.get_conversation_context()
    assert len(context) == 2
    assert isinstance(context[0], HumanMessage)
    assert isinstance(context[1], AIMessage)
    assert context[0].content == "test user message"
    assert context[1].content == "test ai message"

def test_max_history_limit(memory):
    """Test max history limit."""
    # Add more messages than max_history
    for i in range(memory.max_history + 5):
        memory.add_user_message(f"message {i}")
    
    context = memory.get_conversation_context()
    assert len(context) == memory.max_history
    assert context[-1].content == f"message {memory.max_history + 4}"

def test_get_relevant_tool_outputs(memory):
    """Test getting relevant tool outputs."""
    memory.add_tool_memory("test_tool", "test input", "test output")
    memory.add_tool_memory("another_tool", "another input", "another output")
    
    outputs = memory.get_relevant_tool_outputs("test")
    assert len(outputs) == 2  # Currently returns all outputs
    assert outputs[0]["tool"] == "test_tool"
    assert outputs[0]["input"] == "test input"
    assert outputs[0]["output"] == "test output" 