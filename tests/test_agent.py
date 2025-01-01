"""Tests for the agent module."""
import pytest
from unittest.mock import patch, Mock
from src.agent.base import Agent

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    with patch('src.agent.base.ChatOpenAI'):  # Mock the LLM to avoid API calls
        return Agent()

@pytest.mark.asyncio
async def test_process_message_with_memory(agent):
    """Test message processing with memory."""
    # Mock LLM response
    agent.llm.invoke = Mock(return_value=Mock(content="Test response"))
    
    # Process a message
    response = await agent.process_message("test message")
    assert response == "Test response"
    
    # Verify conversation was stored
    assert len(agent.memory.conversation_history) > 0
    assert agent.memory.conversation_history[-1].content == "Test response"

@pytest.mark.asyncio
async def test_search_with_memory(agent):
    """Test search with memory storage."""
    with patch('src.tools.search.SearchTool.search_web') as mock_search:
        # Mock search results
        mock_results = [{"title": "Test", "link": "https://test.com"}]
        mock_search.return_value = mock_results
        
        # Perform search
        results = await agent.search("test query")
        assert results == mock_results
        
        # Verify memory was updated
        assert len(agent._recent_tool_memories) == 1
        tool_memory = agent._recent_tool_memories[0]
        assert tool_memory.tool_name == "search"
        assert tool_memory.input_data == {"query": "test query"}
        assert tool_memory.output_data == mock_results

@pytest.mark.asyncio
async def test_http_request_with_memory(agent):
    """Test HTTP request with memory storage."""
    with patch('src.tools.httprequest.HTTPRequestTool.request') as mock_request:
        # Mock HTTP response
        mock_response = {"status": "ok", "data": "test"}
        mock_request.return_value = mock_response
        
        # Make request
        result = await agent.http_request("https://test.com")
        assert result == mock_response
        
        # Verify memory was updated
        assert len(agent._recent_tool_memories) == 1
        tool_memory = agent._recent_tool_memories[0]
        assert tool_memory.tool_name == "http_request"
        assert tool_memory.input_data == {"url": "https://test.com"}
        assert tool_memory.output_data == mock_response

@pytest.mark.asyncio
async def test_browser_with_memory(agent):
    """Test browser with memory storage."""
    with patch('src.tools.browser.BrowserTool.get_page_content') as mock_browser:
        # Mock page content
        mock_content = "A" * 2000  # Long content
        mock_browser.return_value = mock_content
        
        # Get page content
        content = await agent.get_page_content("https://test.com")
        assert content == mock_content
        
        # Verify memory was updated
        assert len(agent._recent_tool_memories) == 1
        tool_memory = agent._recent_tool_memories[0]
        assert tool_memory.tool_name == "browser"
        assert tool_memory.input_data == {"url": "https://test.com"}
        assert tool_memory.output_data == {"url": "https://test.com", "content": mock_content} 