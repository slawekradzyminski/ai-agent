"""Tests for the agent module."""
import pytest
from unittest.mock import Mock, patch, call
from src.agent.base import Agent

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    return Agent()

@pytest.mark.asyncio
async def test_process_message_with_memory(agent):
    """Test processing a message with memory context."""
    with patch('langchain_openai.ChatOpenAI.invoke') as mock_chat:
        # Mock chat responses
        def mock_invoke(messages):
            mock_response = Mock()
            mock_response.content = "This is a test response."
            return mock_response
        
        mock_chat.side_effect = mock_invoke
        
        # Add a tool output first
        with patch('src.tools.search.SearchTool.search_web') as mock_search:
            mock_search.return_value = [{"title": "Python", "link": "https://python.org"}]
            agent.search("Python")
        
        # First message should include the tool output
        response1 = await agent.process_message(
            "What did you find about Python?",
            system_prompt="You are a helpful AI assistant."
        )
        assert response1 == "This is a test response."
        
        # Second message should include both the previous conversation and tool output
        response2 = await agent.process_message("Tell me more about it")
        assert response2 == "This is a test response."
        
        # Verify context was included in the messages
        calls = mock_chat.call_args_list
        assert len(calls) == 2
        
        # Check first call's context
        first_call_messages = calls[0][0][0]
        context_message = first_call_messages[1].content if len(first_call_messages) > 1 else first_call_messages[0].content
        assert "Previous conversation" in context_message
        assert "Tool Output - search" in context_message
        assert "Python" in context_message

def test_search_with_memory(agent):
    """Test search with memory storage."""
    with patch('src.tools.search.SearchTool.search_web') as mock_search:
        # Mock search results
        mock_results = [{"title": "Test", "link": "https://test.com"}]
        mock_search.return_value = mock_results
        
        # Perform search
        results = agent.search("test query")
        assert results == mock_results
        
        # Verify memory storage
        tool_memory = agent.memory.tool_history[-1]
        assert tool_memory.tool_name == "search"
        assert tool_memory.input_data == {"query": "test query"}
        assert tool_memory.output_data == mock_results

def test_http_request_with_memory(agent):
    """Test HTTP request with memory storage."""
    with patch('src.tools.httprequest.HTTPRequestTool.request') as mock_request:
        # Mock HTTP response
        mock_response = {"status": "ok", "data": "test"}
        mock_request.return_value = mock_response
        
        # Make request
        result = agent.http_request("https://test.com")
        assert result == mock_response
        
        # Verify memory storage
        tool_memory = agent.memory.tool_history[-1]
        assert tool_memory.tool_name == "http_request"
        assert tool_memory.input_data == {"url": "https://test.com"}
        assert tool_memory.output_data == mock_response

def test_browser_with_memory(agent):
    """Test browser with memory storage."""
    with patch('src.tools.browser.BrowserTool.get_page_content') as mock_browser:
        # Mock page content
        mock_content = "A" * 2000  # Long content
        mock_browser.return_value = mock_content
        
        # Get page content
        content = agent.get_page_content("https://test.com")
        assert content == mock_content
        
        # Verify memory storage (should be truncated)
        tool_memory = agent.memory.tool_history[-1]
        assert tool_memory.tool_name == "browser"
        assert tool_memory.input_data == {"url": "https://test.com"}
        assert len(tool_memory.output_data) == 1000  # Truncated
        assert tool_memory.output_data == mock_content[:1000] 