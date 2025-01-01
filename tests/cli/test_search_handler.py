"""Tests for the search command handler."""
import pytest
from unittest.mock import Mock, AsyncMock

from src.cli.handlers.search import SearchHandler

@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent.search = AsyncMock()
    return agent

class TestSearchHandler:
    """Tests for the search command handler."""

    def test_can_handle(self):
        """Test command recognition."""
        handler = SearchHandler(Mock())
        assert handler.can_handle("search: python")
        assert handler.can_handle("SEARCH: python")
        assert not handler.can_handle("http: example.com")
        assert not handler.can_handle("regular message")

    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        """Test search command handling."""
        mock_results = [
            {"title": "Test", "link": "http://test.com", "snippet": "Test snippet"}
        ]
        mock_agent.search.return_value = mock_results
        
        handler = SearchHandler(mock_agent)
        result = await handler.handle("search: python")
        
        mock_agent.search.assert_called_once_with("python")
        assert result == mock_results

    def test_format_results(self, mock_agent):
        """Test search results formatting."""
        handler = SearchHandler(mock_agent)
        results = [
            {
                "title": "Test Title",
                "link": "http://test.com",
                "snippet": "Test snippet",
                "source": "test"
            }
        ]
        
        formatted = handler.format_results("python", results)
        assert "Search Results for: python" in formatted
        assert "Test Title" in formatted
        assert "http://test.com" in formatted
        assert "Test snippet" in formatted 