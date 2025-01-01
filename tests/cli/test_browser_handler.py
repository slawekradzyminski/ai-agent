"""Tests for the browser command handler."""
import pytest
from unittest.mock import Mock, AsyncMock

from src.cli.handlers.browser import BrowserHandler

@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent.get_page_content = AsyncMock()
    return agent

class TestBrowserHandler:
    """Tests for the browser command handler."""

    def test_can_handle(self):
        """Test command recognition."""
        handler = BrowserHandler(Mock())
        assert handler.can_handle("browser: example.com")
        assert handler.can_handle("BROWSER: example.com")
        assert not handler.can_handle("search: python")
        assert not handler.can_handle("regular message")

    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        """Test browser command handling."""
        mock_content = "Page content"
        mock_agent.get_page_content.return_value = mock_content
        
        handler = BrowserHandler(mock_agent)
        result = await handler.handle("browser: example.com")
        
        mock_agent.get_page_content.assert_called_once_with("example.com")
        assert result == mock_content

    def test_format_result(self, mock_agent):
        """Test browser result formatting."""
        handler = BrowserHandler(mock_agent)
        content = "A" * 1000  # Long content
        
        formatted = handler.format_result("example.com", content)
        assert "Page Content from example.com" in formatted
        assert len(formatted.split("\n")[-1]) <= 503  # 500 chars + "..."
        assert "..." in formatted 