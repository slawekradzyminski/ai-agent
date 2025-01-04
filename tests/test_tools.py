"""Tests for the tools module."""
import pytest
from unittest.mock import patch, Mock
from src.tools.search import SearchTool
from src.tools.http import HttpTool
from src.tools.browser import BrowserTool

@pytest.fixture
def search_tool():
    """Create a search tool instance for testing."""
    return SearchTool()

@pytest.fixture
def http_tool():
    """Create an HTTP tool instance for testing."""
    return HttpTool()

@pytest.fixture
def browser_tool():
    """Create a browser tool instance for testing."""
    return BrowserTool()

def test_search_web(search_tool):
    """Test web search functionality."""
    with patch.object(search_tool.ddgs, 'text') as mock_search:
        # Mock search results
        mock_results = [
            {
                "title": "Test Result",
                "link": "https://test.com",
                "snippet": "Test snippet"
            }
        ]
        mock_search.return_value = mock_results

        results = search_tool.search_web("test query")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["title"] == "Test Result"

def test_search_web_empty_results(search_tool):
    """Test web search with no results."""
    with patch.object(search_tool.ddgs, 'text') as mock_search:
        # Mock empty search results
        mock_search.return_value = []

        results = search_tool.search_web("nonexistent query")
        assert isinstance(results, list)
        assert len(results) == 0

def test_search_web_error_handling(search_tool):
    """Test web search error handling."""
    with patch.object(search_tool.ddgs, 'text') as mock_search:
        # Mock search error
        mock_search.side_effect = Exception("Search failed")

        results = search_tool.search_web("error query")
        assert isinstance(results, list)
        assert len(results) == 0 