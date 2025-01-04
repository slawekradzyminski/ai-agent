"""Tests for the context builder module."""
import pytest
from unittest.mock import Mock, patch
from src.context.builder import ContextBuilder
from src.memory.memory import Memory
from src.tools.search import SearchTool
from src.tools.browser import BrowserTool
from src.tools.httprequest import HTTPRequestTool

@pytest.fixture
def context_builder():
    """Create a context builder instance for testing."""
    memory = Memory()
    search_tool = SearchTool()
    browser_tool = BrowserTool()
    http_tool = HTTPRequestTool()
    return ContextBuilder(memory, search_tool, browser_tool, http_tool)

@pytest.mark.asyncio
async def test_build_context(context_builder):
    """Test building context with search results and content."""
    mock_search_results = [
        {
            "title": "Test Result",
            "link": "https://test.com",
            "snippet": "Test snippet"
        },
        {
            "title": "Test Result 2",
            "link": "https://test2.com",
            "snippet": "Test snippet 2"
        }
    ]
    context_builder.search_tool.search_web = Mock(return_value=mock_search_results)
    mock_browser_content = "Test page content"
    context_builder.browser_tool.get_page_content = Mock(return_value=mock_browser_content)
    mock_http_response = {
        'status_code': 200,
        'content_type': 'application/json',
        'data': {'test': 'data'}
    }
    context_builder.http_tool.request = Mock(return_value=mock_http_response)
    
    context, tool_memories = await context_builder.build_context("test query")
    
    assert "Search Results:" in context
    assert "Content from https://test.com" in context
    assert "Content from https://test2.com" in context
    assert mock_browser_content in context
    assert len(tool_memories) > 0
    assert any(mem.tool_name == "search" for mem in tool_memories)
    assert any(mem.tool_name == "browser" for mem in tool_memories)

@pytest.mark.asyncio
async def test_build_context_no_results(context_builder):
    """Test building context with no search results."""
    context_builder.search_tool.search_web = Mock(return_value=[])
    
    context, tool_memories = await context_builder.build_context("test query")
    
    assert context == ""
    assert len(tool_memories) == 0

@pytest.mark.asyncio
async def test_build_context_browser_fallback(context_builder):
    """Test building context with browser fallback to HTTP."""
    mock_search_results = [
        {
            "title": "Test Result",
            "link": "https://test.com",
            "snippet": "Test snippet"
        }
    ]
    context_builder.search_tool.search_web = Mock(return_value=mock_search_results)
    context_builder.browser_tool.get_page_content = Mock(side_effect=Exception("Browser failed"))
    mock_http_response = {
        'status_code': 200,
        'content_type': 'text/plain',
        'data': {'content': 'Test content', 'content_type': 'text/plain'}
    }
    context_builder.http_tool.request = Mock(return_value=mock_http_response)
    
    context, tool_memories = await context_builder.build_context("test query")
    
    assert "Search Results:" in context
    assert "Content from https://test.com" in context
    assert "Test content" in context
    assert len(tool_memories) == 2
    assert tool_memories[0].tool_name == "search"
    assert tool_memories[1].tool_name == "http_request"

def test_format_tool_context(context_builder):
    """Test formatting tool memories into context string."""
    tool_memories = [
        Mock(
            tool_name="browser",
            output_data={"url": "https://test.com", "content": "Test content"}
        ),
        Mock(
            tool_name="search",
            output_data={"results": ["result1", "result2"]}
        )
    ]
    
    context = context_builder.format_tool_context(tool_memories)
    
    assert "Recent tool outputs:" in context
    assert "Browser content from https://test.com" in context
    assert "Test content" in context
    assert "search output:" in context
    assert "result1" in context
    assert "result2" in context

def test_format_tool_context_empty(context_builder):
    """Test formatting empty tool memories."""
    context = context_builder.format_tool_context([])
    assert context == "" 