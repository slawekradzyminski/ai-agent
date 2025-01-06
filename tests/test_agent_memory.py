import pytest
from unittest.mock import patch, Mock, AsyncMock
from src.agent.base import Agent
from langchain_core.callbacks import CallbackManagerForToolRun

@pytest.fixture
def agent():
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
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    
    mock_callback_manager = Mock(spec=CallbackManagerForToolRun)
    mock_callback_manager.on_tool_end = Mock()
    
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
    
    await agent.get_page_content("test.com")
    
    tool_outputs = agent.memory.get_relevant_tool_outputs("test.com")
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == "browser"
    assert tool_outputs[0]["input"] == "test.com"
    assert "test content" in tool_outputs[0]["output"]

@pytest.mark.asyncio
async def test_browser_content_in_message_context(agent):
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    
    mock_callback_manager = Mock(spec=CallbackManagerForToolRun)
    mock_callback_manager.on_tool_end = Mock()
    
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
    
    await agent.get_page_content("test.com")
    await agent.process_message("What did you find?")
    
    tool_outputs = agent.memory.get_relevant_tool_outputs("What did you find?")
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == "browser"
    assert "test content" in tool_outputs[0]["output"]

@pytest.mark.asyncio
async def test_multiple_tool_outputs_in_context(agent):
    browser_tool = next(tool for tool in agent.tools if tool.name == "browser")
    search_tool = next(tool for tool in agent.tools if tool.name == "search")
    
    mock_callback_manager = Mock(spec=CallbackManagerForToolRun)
    mock_callback_manager.on_tool_end = Mock()
    
    async def mock_browser_arun(url, run_manager=None, **kwargs):
        result = {"content": "test content", "url": "test.com"}
        if run_manager:
            await run_manager.on_tool_end(
                str(result),
                tool_input=url,
                tool_name="browser"
            )
        return result
    
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
    
    await agent.get_page_content("test.com")
    await agent.search("test query")
    
    tool_outputs = agent.memory.get_relevant_tool_outputs("")
    assert len(tool_outputs) == 2
    assert any(output["tool"] == "browser" for output in tool_outputs)
    assert any(output["tool"] == "search" for output in tool_outputs) 