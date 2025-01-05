"""Tests for callback handlers."""
import pytest
from unittest.mock import Mock
from src.callbacks.tool_output import ToolOutputCallbackHandler
from src.memory.vector_memory import VectorMemory

@pytest.fixture
def memory():
    """Create a memory instance for testing."""
    return VectorMemory()

@pytest.fixture
def callback_handler(memory):
    """Create a callback handler instance for testing."""
    return ToolOutputCallbackHandler(memory)

def test_tool_output_callback_initialization(callback_handler):
    """Test callback handler initialization."""
    assert callback_handler.memory is not None
    assert isinstance(callback_handler.memory, VectorMemory)

@pytest.mark.asyncio
async def test_on_tool_end(callback_handler):
    """Test tool output storage on tool end."""
    # Test data
    tool_name = "test_tool"
    tool_input = "test input"
    tool_output = "test output"
    
    # Call on_tool_end
    await callback_handler.on_tool_end(
        tool_output,
        tool_name=tool_name,
        tool_input=tool_input
    )
    
    # Verify tool output was stored
    tool_outputs = callback_handler.memory.get_relevant_tool_outputs(tool_input)
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == tool_name
    assert tool_outputs[0]["input"] == tool_input
    assert tool_outputs[0]["output"] == tool_output

@pytest.mark.asyncio
async def test_on_tool_end_with_complex_output(callback_handler):
    """Test tool output storage with complex output types."""
    # Test data
    tool_name = "test_tool"
    tool_input = "test input"
    tool_output = {"key": "value", "nested": {"data": 123}}
    
    # Call on_tool_end
    await callback_handler.on_tool_end(
        tool_output,
        tool_name=tool_name,
        tool_input=tool_input
    )
    
    # Verify tool output was stored
    tool_outputs = callback_handler.memory.get_relevant_tool_outputs(tool_input)
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == tool_name
    assert tool_outputs[0]["input"] == tool_input
    assert "value" in tool_outputs[0]["output"]
    assert "123" in tool_outputs[0]["output"]

@pytest.mark.asyncio
async def test_on_tool_end_with_empty_output(callback_handler):
    """Test tool output storage with empty output."""
    # Test data
    tool_name = "test_tool"
    tool_input = "test input"
    tool_output = ""
    
    # Call on_tool_end
    await callback_handler.on_tool_end(
        tool_output,
        tool_name=tool_name,
        tool_input=tool_input
    )
    
    # Verify tool output was stored
    tool_outputs = callback_handler.memory.get_relevant_tool_outputs(tool_input)
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == tool_name
    assert tool_outputs[0]["input"] == tool_input
    assert tool_outputs[0]["output"] == "" 