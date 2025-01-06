import pytest
from unittest.mock import Mock
from src.callbacks.tool_output import ToolOutputCallbackHandler
from src.memory.vector_memory import VectorMemory

@pytest.fixture
def memory():
    return VectorMemory()

@pytest.fixture
def callback_handler(memory):
    return ToolOutputCallbackHandler(memory)

def test_tool_output_callback_initialization(callback_handler):
    assert callback_handler.memory is not None
    assert isinstance(callback_handler.memory, VectorMemory)

@pytest.mark.asyncio
async def test_on_tool_end(callback_handler):
    tool_name = "test_tool"
    tool_input = "test input"
    tool_output = "test output"
    
    await callback_handler.on_tool_end(
        tool_output,
        tool_name=tool_name,
        tool_input=tool_input
    )
    
    tool_outputs = callback_handler.memory.get_relevant_tool_outputs(tool_input)
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == tool_name
    assert tool_outputs[0]["input"] == tool_input
    assert tool_outputs[0]["output"] == tool_output

@pytest.mark.asyncio
async def test_on_tool_end_with_complex_output(callback_handler):
    tool_name = "test_tool"
    tool_input = "test input"
    tool_output = {"key": "value", "nested": {"data": 123}}
    
    await callback_handler.on_tool_end(
        tool_output,
        tool_name=tool_name,
        tool_input=tool_input
    )
    
    tool_outputs = callback_handler.memory.get_relevant_tool_outputs(tool_input)
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == tool_name
    assert tool_outputs[0]["input"] == tool_input
    assert "value" in tool_outputs[0]["output"]
    assert "123" in tool_outputs[0]["output"]

@pytest.mark.asyncio
async def test_on_tool_end_with_empty_output(callback_handler):
    tool_name = "test_tool"
    tool_input = "test input"
    tool_output = ""
    
    await callback_handler.on_tool_end(
        tool_output,
        tool_name=tool_name,
        tool_input=tool_input
    )
    
    tool_outputs = callback_handler.memory.get_relevant_tool_outputs(tool_input)
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == tool_name
    assert tool_outputs[0]["input"] == tool_input
    assert tool_outputs[0]["output"] == "" 