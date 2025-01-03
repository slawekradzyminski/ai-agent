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
        content = "A" * 1000  # Long content
        
        # Test truncation of long content
        formatted = handler.format_result(content)
        assert len(formatted) < len(content)
        assert formatted.endswith("...")
        
        # Test error message
        error_msg = "Error: Browser request failed"
        formatted = handler.format_result(error_msg)
        assert formatted == error_msg
        
        # Test empty content
        formatted = handler.format_result("")
        assert formatted == "No content retrieved" 