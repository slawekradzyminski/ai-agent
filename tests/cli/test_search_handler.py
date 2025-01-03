"""Tests for the search command handler."""
import pytest
from unittest.mock import Mock, AsyncMock
from src.cli.handlers.search import SearchHandler

class TestSearchHandler:
    """Tests for the SearchHandler class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = Mock()
        agent.search = AsyncMock()
        return agent

    def test_can_handle(self):
        """Test command recognition."""
        handler = SearchHandler(Mock())
        assert handler.can_handle("search: python")
        assert handler.can_handle("SEARCH: python")
        assert not handler.can_handle("browser: example.com")

    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        """Test search command handling."""
        handler = SearchHandler(mock_agent)
        mock_results = [{"title": "Test", "link": "http://test.com"}]
        mock_agent.search.return_value = mock_results
        
        result = await handler.handle("search: python")
        assert result == mock_results
        mock_agent.search.assert_called_once_with("python")

    def test_format_results(self, mock_agent):
        """Test search results formatting."""
        handler = SearchHandler(mock_agent)
        
        # Test normal results
        results = [
            {
                "title": "Test Title",
                "link": "http://test.com"
            }
        ]
        formatted = handler.format_results(results)
        assert "Test Title" in formatted
        assert "http://test.com" in formatted
        
        # Test empty results
        formatted = handler.format_results([])
        assert formatted == "No results found"
        
        # Test error results
        error_results = [{"error": "Search failed"}]
        formatted = handler.format_results(error_results)
        assert formatted == "Error: Search failed" 