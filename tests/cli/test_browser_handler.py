"""Tests for the browser command handler."""
import pytest
from unittest.mock import Mock, AsyncMock
from src.cli.handlers.browser import BrowserHandler

class TestBrowserHandler:
    """Tests for the BrowserHandler class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = Mock()
        agent.get_page_content = AsyncMock()
        return agent

    def test_can_handle(self):
        """Test command recognition."""
        handler = BrowserHandler(Mock())
        assert handler.can_handle("browser: example.com")
        assert handler.can_handle("BROWSER: example.com")
        assert not handler.can_handle("search: example.com")

    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        """Test browser command handling."""
        handler = BrowserHandler(mock_agent)
        mock_agent.get_page_content.return_value = "Test content"
        
        result = await handler.handle("browser: example.com")
        assert result == "Test content"
        mock_agent.get_page_content.assert_called_once_with("example.com")

    def test_format_result(self, mock_agent):
        """Test browser result formatting."""
        handler = BrowserHandler(mock_agent)
        
        # Test successful response
        content = "A" * 1000  # Long content
        result = {"url": "test.com", "content": content}
        formatted = handler.format_result(result)
        assert len(formatted) < len(content) + 100  # Account for URL and formatting
        assert formatted.endswith("...")
        
        # Test error response
        error_result = {"error": "Browser request failed"}
        formatted = handler.format_result(error_result)
        assert "Error" in formatted
        
        # Test empty response
        formatted = handler.format_result({})
        assert "No content retrieved" in formatted 