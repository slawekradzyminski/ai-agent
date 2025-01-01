"""Tests for the search tool."""
import pytest
from unittest.mock import patch, Mock
from src.tools.search import SearchTool

@pytest.fixture
def search_tool():
    """Create a search tool instance for testing."""
    return SearchTool()

def test_search_web(search_tool):
    """Test web search functionality."""
    with patch('langchain_community.utilities.DuckDuckGoSearchAPIWrapper.results') as mock_search:
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
        assert results[0]["link"] == "https://test.com"
        assert results[0]["snippet"] == "Test snippet"

def test_search_web_empty_results(search_tool):
    """Test web search with no results."""
    with patch('langchain_community.utilities.DuckDuckGoSearchAPIWrapper.results') as mock_search:
        # Mock empty search results
        mock_search.return_value = []
        
        results = search_tool.search_web("nonexistent query")
        assert isinstance(results, list)
        assert len(results) == 0

def test_search_web_error_handling(search_tool):
    """Test web search error handling."""
    with patch('langchain_community.utilities.DuckDuckGoSearchAPIWrapper.results') as mock_search:
        # Mock search error
        mock_search.side_effect = Exception("Search failed")
        
        results = search_tool.search_web("error query")
        assert isinstance(results, list)
        assert len(results) == 0 