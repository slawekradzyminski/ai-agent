"""Tests for the agent module."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.agent.base import Agent
from src.callbacks.tool_output import ToolOutputCallbackHandler

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    with patch('src.agent.base.ChatOpenAI'), \
         patch('src.agent.base.create_openai_functions_agent'), \
         patch('src.agent.base.AgentExecutor') as mock_executor_class:
        # Mock the agent executor
        mock_executor = Mock()
        mock_executor.ainvoke = AsyncMock(return_value={"output": "test response"})
        mock_executor_class.return_value = mock_executor
        
        # Create the agent
        agent = Agent(openai_api_key="test-key")
        
        # Ensure callbacks are properly set
        mock_executor.callbacks = [ToolOutputCallbackHandler(agent.memory)]
        
        return agent

@pytest.mark.asyncio
async def test_process_message_with_tool_selection(agent):
    """Test processing a message that requires tool selection."""
    response = await agent.process_message("Search for test query")
    assert response == "test response"
    agent.agent_executor.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_with_multiple_tools(agent):
    """Test processing a message that uses multiple tools."""
    response = await agent.process_message("Search and browse test.com")
    assert response == "test response"
    agent.agent_executor.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_error_handling(agent):
    """Test error handling in message processing."""
    agent.agent_executor.ainvoke.side_effect = Exception("Test error")
    response = await agent.process_message("Test message")
    assert "error" in response.lower()
    agent.agent_executor.ainvoke.assert_called_once()

def test_tool_descriptions(agent):
    """Test that tools have proper descriptions."""
    for tool in agent.tools:
        assert tool.name is not None
        assert tool.description is not None

@pytest.mark.asyncio
async def test_autonomous_tool_output_storage(agent):
    """Test that tool outputs are stored when used autonomously."""
    # Mock tool usage in agent executor
    tool_name = "search"
    tool_input = "weather in London"
    tool_output = "Cloudy with a chance of rain"
    
    async def mock_ainvoke(inputs):
        # Simulate tool usage via callback
        callback = agent.agent_executor.callbacks[0]
        await callback.on_tool_end(
            tool_output,
            tool_name=tool_name,
            tool_input=tool_input
        )
        return {"output": "It's cloudy in London"}
    
    agent.agent_executor.ainvoke = AsyncMock(side_effect=mock_ainvoke)
    
    # Process message that should trigger tool usage
    await agent.process_message("What's the weather in London?")
    
    # Verify tool output was stored
    tool_outputs = agent.memory.get_relevant_tool_outputs("weather London")
    assert len(tool_outputs) > 0
    assert any(
        output["tool"] == tool_name and
        output["input"] == tool_input and
        output["output"] == tool_output
        for output in tool_outputs
    ) 