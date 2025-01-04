"""Tests for the agent module."""
import pytest
from unittest.mock import patch, Mock, AsyncMock, ANY
from langchain.schema import AgentAction, AgentFinish
from src.agent.base import Agent
from src.memory.memory import Memory

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    with patch('langchain_openai.ChatOpenAI') as mock_llm, \
         patch('selenium.webdriver.chrome.options.Options') as mock_options, \
         patch('selenium.webdriver.Chrome') as mock_driver, \
         patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait, \
         patch('langchain.agents.create_openai_functions_agent') as mock_create_agent:
        
        # Mock the agent creation
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        agent_instance = Agent()
        
        # Mock the agent executor after initialization
        mock_executor = AsyncMock()
        mock_executor.ainvoke = AsyncMock(return_value={"output": "Test response"})
        agent_instance._agent_executor = mock_executor
        
        return agent_instance

@pytest.mark.asyncio
async def test_process_message_with_tool_selection(agent):
    """Test message processing with autonomous tool selection."""
    response = await agent.process_message("What is Python?")
    
    # Verify the agent executor was called with both input and chat_history
    agent.agent_executor.ainvoke.assert_called_once_with(
        {
            "input": "What is Python?",
            "chat_history": ANY  # Chat history can be empty list or messages
        },
        {"request_id": ANY}
    )
    
    assert response == "Test response"
    assert len(agent.memory.conversation_history) > 0
    assert agent.memory.conversation_history[-1].content == "Test response"

@pytest.mark.asyncio
async def test_process_message_with_multiple_tools(agent):
    """Test message processing with multiple tool usage."""
    # Mock the agent to use multiple tools
    agent.agent_executor.ainvoke = AsyncMock(return_value={"output": "Combined response from search and browser"})
    
    response = await agent.process_message("Tell me about Python and show me python.org")
    
    assert response == "Combined response from search and browser"
    assert len(agent.memory.conversation_history) > 0

@pytest.mark.asyncio
async def test_process_message_error_handling(agent):
    """Test error handling in message processing."""
    agent.agent_executor.ainvoke = AsyncMock(side_effect=Exception("Tool execution failed"))
    
    with pytest.raises(Exception) as exc_info:
        await agent.process_message("test query")
    
    assert str(exc_info.value) == "Tool execution failed"

@pytest.mark.asyncio
async def test_tool_descriptions():
    """Test that tools have appropriate descriptions for the agent."""
    with patch('langchain_openai.ChatOpenAI'), \
         patch('selenium.webdriver.chrome.options.Options'), \
         patch('selenium.webdriver.Chrome'), \
         patch('selenium.webdriver.support.ui.WebDriverWait'), \
         patch('langchain.agents.create_openai_functions_agent'):
        
        agent = Agent()
        
        # Verify tool descriptions
        tool_names = {tool.name for tool in agent.tools}
        assert "web_search" in tool_names
        assert "http_request" in tool_names
        assert "browser" in tool_names
        
        # Verify each tool has a meaningful description
        for tool in agent.tools:
            assert len(tool.description) > 0
            assert tool.description.endswith(".")  # Proper sentence
            assert "Use this when" in tool.description  # Usage guidance 