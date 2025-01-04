"""Test context builder module."""
import pytest
from unittest.mock import Mock
from src.memory.vector_memory import VectorMemory

@pytest.fixture
def memory():
    """Create a memory instance for testing."""
    return VectorMemory()

@pytest.fixture
def mock_messages():
    """Create mock messages for testing."""
    return [
        Mock(content="Hello"),
        Mock(content="Hi there"),
        Mock(content="How are you?")
    ]

def test_memory_initialization(memory):
    """Test memory initialization."""
    assert memory.memory_key == "chat_history"
    assert memory.return_messages is True
    assert memory.max_history == 10

def test_memory_variables(memory):
    """Test memory variables."""
    variables = memory.memory_variables
    assert "chat_history" in variables
    assert "tool_history" in variables

def test_add_user_message(memory):
    """Test adding user message."""
    memory.add_user_message("test message")
    assert len(memory._documents) == 1
    assert len(memory._messages) == 1
    assert memory._documents[0] == "test message"
    assert memory._metadatas[0]["type"] == "conversation"
    assert memory._metadatas[0]["is_user"] is True

def test_add_ai_message(memory):
    """Test adding AI message."""
    memory.add_ai_message("test response")
    assert len(memory._documents) == 1
    assert len(memory._messages) == 1
    assert memory._documents[0] == "test response"
    assert memory._metadatas[0]["type"] == "conversation"
    assert memory._metadatas[0]["is_user"] is False

def test_add_tool_memory(memory):
    """Test adding tool memory."""
    memory.add_tool_memory("test_tool", "input", "output")
    assert len(memory._documents) == 1
    assert len(memory._tool_outputs) == 1
    assert memory._documents[0] == "test_tool: input -> output"
    assert memory._metadatas[0]["type"] == "tool"
    assert memory._metadatas[0]["tool_name"] == "test_tool"

def test_get_conversation_context(memory, mock_messages):
    """Test getting conversation context."""
    for msg in mock_messages:
        memory._messages.append(msg)
    context = memory.get_conversation_context()
    assert len(context) == len(mock_messages)
    assert all(msg in context for msg in mock_messages)

def test_clear_memory(memory):
    """Test clearing memory."""
    memory.add_user_message("test")
    memory.add_ai_message("response")
    memory.add_tool_memory("tool", "input", "output")
    
    memory.clear()
    assert len(memory._documents) == 0
    assert len(memory._messages) == 0
    assert len(memory._tool_outputs) == 0
    assert memory._vectors is None 