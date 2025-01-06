import pytest
from unittest.mock import Mock, AsyncMock
from src.cli.handlers.search import SearchHandler

class TestSearchHandler:
    @pytest.fixture
    def mock_agent(self):
        agent = Mock()
        agent.search = AsyncMock()
        return agent

    def test_can_handle(self):
        handler = SearchHandler(Mock())
        assert handler.can_handle("search: python")
        assert handler.can_handle("SEARCH: python")
        assert not handler.can_handle("browser: example.com")

    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        handler = SearchHandler(mock_agent)
        mock_results = [{"title": "Test", "link": "http://test.com"}]
        mock_agent.search.return_value = mock_results
        
        result = await handler.handle("search: python")
        assert result == mock_results
        mock_agent.search.assert_called_once_with("python")

    def test_format_results(self, mock_agent):
        handler = SearchHandler(mock_agent)
        
        results = [
            {
                "title": "Test Title",
                "link": "http://test.com"
            }
        ]
        formatted = handler.format_results(results)
        assert "Test Title" in formatted
        assert "http://test.com" in formatted
        
        formatted = handler.format_results([])
        assert formatted == "No results found"
        
        error_results = [{"error": "Search failed"}]
        formatted = handler.format_results(error_results)
        assert formatted == "Error: Search failed" 