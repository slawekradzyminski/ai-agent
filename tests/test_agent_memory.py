"""Test agent memory integration."""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from src.agent.base import Agent

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    with patch('langchain_openai.ChatOpenAI') as mock_llm, \
         patch('selenium.webdriver.chrome.options.Options') as mock_options, \
         patch('selenium.webdriver.Chrome') as mock_driver, \
         patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait, \
         patch('langchain.agents.create_openai_functions_agent') as mock_create_agent, \
         patch('langchain.agents.agent.AgentExecutor') as mock_executor:
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        mock_executor_instance = AsyncMock()
        mock_executor_instance.ainvoke.return_value = {"output": "test response"}
        mock_executor.return_value = mock_executor_instance
        
        agent_instance = Agent(openai_api_key="test-key")
        return agent_instance

@pytest.mark.asyncio
async def test_browser_content_memory_storage(agent):
    """Test that browser content is stored in memory."""
    # Mock browser tool to return test content
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    browser_tool._arun = AsyncMock(return_value={"content": "test content", "url": "test.com"})
    
    await agent.get_page_content("test.com")
    
    # Check that tool output is stored
    assert len(agent.memory.tool_outputs) == 1
    assert agent.memory.tool_outputs[0].tool_name == "browser"
    assert agent.memory.tool_outputs[0].input == "test.com"
    assert "test content" in agent.memory.tool_outputs[0].output

@pytest.mark.asyncio
async def test_browser_content_in_message_context(agent):
    """Test that browser content is included in message context."""
    # Mock browser tool to return test content
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    browser_tool._arun = AsyncMock(return_value={"content": "test content", "url": "test.com"})
    
    await agent.get_page_content("test.com")
    await agent.process_message("What did you find?")
    
    # Check that tool output is included in context
    tool_outputs = agent.memory.get_relevant_tool_outputs("What did you find?")
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == "browser"
    assert "test content" in tool_outputs[0]["output"]

@pytest.mark.asyncio
async def test_multiple_tool_outputs_in_context(agent):
    """Test that multiple tool outputs are included in context."""
    # Mock tools to return test content
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    browser_tool._arun = AsyncMock(return_value={"content": "test content", "url": "test.com"})
    
    search_tool = next(tool for tool in agent.tools if tool.name == "search")
    search_tool._arun = AsyncMock(return_value=["search result 1", "search result 2"])
    
    # Use both tools
    await agent.get_page_content("test.com")
    await agent.search("test query")
    
    # Check that both tool outputs are stored
    assert len(agent.memory.tool_outputs) == 2
    assert any(output.tool_name == "browser" for output in agent.memory.tool_outputs)
    assert any(output.tool_name == "search" for output in agent.memory.tool_outputs) 