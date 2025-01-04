"""Test agent module."""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from src.agent.base import Agent
from src.tools.browser import BrowserTool
from src.tools.search import SearchTool
from src.tools.http import HttpTool

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    with patch('langchain_openai.ChatOpenAI') as mock_llm_class, \
         patch('selenium.webdriver.chrome.options.Options') as mock_options, \
         patch('selenium.webdriver.Chrome') as mock_driver, \
         patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait, \
         patch('langchain.agents.create_openai_functions_agent') as mock_create_agent, \
         patch('langchain.agents.agent.AgentExecutor') as mock_executor:
        
        # Mock the LLM
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock the agent creation
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        # Mock the executor
        mock_executor_instance = Mock()
        mock_executor_instance.ainvoke = AsyncMock(return_value={"output": "test response"})
        mock_executor.return_value = mock_executor_instance
        
        agent_instance = Agent(openai_api_key="test-key")
        agent_instance.agent_executor = mock_executor_instance  # Directly set the mock executor
        return agent_instance

@pytest.mark.asyncio
async def test_process_message_with_tool_selection(agent):
    """Test processing a message that requires tool selection."""
    response = await agent.process_message("Search for test query")
    assert response == "test response"
    assert len(agent.memory.messages) == 2  # User message and AI response

@pytest.mark.asyncio
async def test_process_message_with_multiple_tools(agent):
    """Test processing a message that uses multiple tools."""
    response = await agent.process_message("Search and browse test.com")
    assert response == "test response"
    assert len(agent.memory.messages) == 2

@pytest.mark.asyncio
async def test_process_message_error_handling(agent):
    """Test error handling in message processing."""
    agent.agent_executor.ainvoke = AsyncMock(side_effect=Exception("Test error"))
    response = await agent.process_message("Test message")
    assert "An error occurred" in response
    assert len(agent.memory.messages) == 2  # Error message should be stored

def test_tool_descriptions():
    """Test that tools have appropriate descriptions for the agent."""
    with patch('langchain_openai.ChatOpenAI') as mock_llm_class, \
         patch('selenium.webdriver.chrome.options.Options'), \
         patch('selenium.webdriver.Chrome'), \
         patch('selenium.webdriver.support.ui.WebDriverWait'), \
         patch('langchain.agents.create_openai_functions_agent'), \
         patch('langchain.agents.agent.AgentExecutor'):
        
        # Mock the LLM
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        agent = Agent(openai_api_key="test-key")
        
        # Check that all tools are initialized
        assert len(agent.tools) == 3
        assert any(isinstance(tool, SearchTool) for tool in agent.tools)
        assert any(isinstance(tool, BrowserTool) for tool in agent.tools)
        assert any(isinstance(tool, HttpTool) for tool in agent.tools)
        
        # Check tool descriptions
        for tool in agent.tools:
            assert tool.name
            assert tool.description
            assert callable(tool._arun) 