"""Tests for agent memory functionality."""
import pytest
from unittest.mock import patch, Mock, AsyncMock
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
async def test_browser_content_memory_storage(agent):
    """Test storing browser content in memory."""
    # Mock browser content
    mock_content = "Test webpage content"
    agent.browser_tool.get_page_content = Mock(return_value=mock_content)
    
    # Use the tool via agent
    response = await agent.process_message("Show me content from https://test.com")
    
    # Verify memory storage
    assert len(agent.memory.conversation_history) > 0
    assert response == "Test response"

@pytest.mark.asyncio
async def test_browser_content_in_message_context(agent):
    """Test browser content is included in message context."""
    # Mock browser content
    mock_content = "Test webpage content"
    agent.browser_tool.get_page_content = Mock(return_value=mock_content)
    
    # First message to store content
    await agent.process_message("Show me content from https://test.com")
    
    # Second message to verify context
    response = await agent.process_message("What was in the previous content?")
    
    assert response == "Test response"
    assert len(agent.memory.conversation_history) > 1

@pytest.mark.asyncio
async def test_multiple_tool_outputs_in_context(agent):
    """Test multiple tool outputs are stored and accessible."""
    # Mock tool outputs
    agent.search_tool.search_web = Mock(return_value=[{"title": "Test", "link": "https://test.com"}])
    agent.browser_tool.get_page_content = Mock(return_value="Test content")
    agent.http_tool.request = Mock(return_value={"status": "ok", "data": "Test data"})
    
    # Use multiple tools via agent
    response = await agent.process_message("Search and show me test.com")
    
    assert response == "Test response"
    assert len(agent.memory.conversation_history) > 0 