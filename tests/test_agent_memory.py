"""Test agent memory integration."""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from src.agent.base import Agent
from langchain_core.callbacks import CallbackManagerForToolRun

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
    
    # Create a mock callback manager
    mock_callback_manager = Mock(spec=CallbackManagerForToolRun)
    mock_callback_manager.on_tool_end = Mock()
    
    # Mock the tool's _arun method
    async def mock_arun(url, run_manager=None, **kwargs):
        result = {"content": "test content", "url": "test.com"}
        if run_manager:
            await run_manager.on_tool_end(
                str(result),
                tool_input=url,
                tool_name="browser"
            )
        return result
    
    browser_tool._arun = mock_arun
    
    # Use the tool
    await agent.get_page_content("test.com")
    
    # Check that tool output is stored
    tool_outputs = agent.memory.get_relevant_tool_outputs("test.com")
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == "browser"
    assert tool_outputs[0]["input"] == "test.com"
    assert "test content" in tool_outputs[0]["output"]

@pytest.mark.asyncio
async def test_browser_content_in_message_context(agent):
    """Test that browser content is included in message context."""
    # Mock browser tool to return test content
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    
    # Create a mock callback manager
    mock_callback_manager = Mock(spec=CallbackManagerForToolRun)
    mock_callback_manager.on_tool_end = Mock()
    
    # Mock the tool's _arun method
    async def mock_arun(url, run_manager=None, **kwargs):
        result = {"content": "test content", "url": "test.com"}
        if run_manager:
            await run_manager.on_tool_end(
                str(result),
                tool_input=url,
                tool_name="browser"
            )
        return result
    
    browser_tool._arun = mock_arun
    
    # Use the tool and process a message
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
    search_tool = next(tool for tool in agent.tools if tool.name == "search")
    
    # Create mock callback managers
    mock_callback_manager = Mock(spec=CallbackManagerForToolRun)
    mock_callback_manager.on_tool_end = Mock()
    
    # Mock the browser tool's _arun method
    async def mock_browser_arun(url, run_manager=None, **kwargs):
        result = {"content": "test content", "url": "test.com"}
        if run_manager:
            await run_manager.on_tool_end(
                str(result),
                tool_input=url,
                tool_name="browser"
            )
        return result
    
    # Mock the search tool's _arun method
    async def mock_search_arun(query, run_manager=None, **kwargs):
        result = ["search result 1", "search result 2"]
        if run_manager:
            await run_manager.on_tool_end(
                str(result),
                tool_input=query,
                tool_name="search"
            )
        return result
    
    browser_tool._arun = mock_browser_arun
    search_tool._arun = mock_search_arun
    
    # Use both tools
    await agent.get_page_content("test.com")
    await agent.search("test query")
    
    # Check that both tool outputs are stored
    tool_outputs = agent.memory.get_relevant_tool_outputs("")  # Empty query to get all outputs
    assert len(tool_outputs) == 2
    assert any(output["tool"] == "browser" for output in tool_outputs)
    assert any(output["tool"] == "search" for output in tool_outputs) 