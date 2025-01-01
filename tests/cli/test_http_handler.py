"""Tests for the HTTP command handler."""
import json
import pytest
from unittest.mock import Mock, AsyncMock

from src.cli.handlers.http import HttpHandler

@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent.http_request = AsyncMock()
    return agent

class TestHttpHandler:
    """Tests for the HTTP command handler."""

    def test_can_handle(self):
        """Test command recognition."""
        handler = HttpHandler(Mock())
        assert handler.can_handle("http: example.com")
        assert handler.can_handle("HTTP: example.com")
        assert not handler.can_handle("search: python")
        assert not handler.can_handle("regular message")

    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        """Test HTTP command handling."""
        mock_response = {"status": "ok", "data": "test"}
        mock_agent.http_request.return_value = mock_response
        
        handler = HttpHandler(mock_agent)
        result = await handler.handle("http: example.com")
        
        mock_agent.http_request.assert_called_once_with("example.com")
        assert result == mock_response

    def test_format_result(self, mock_agent):
        """Test HTTP result formatting."""
        handler = HttpHandler(mock_agent)
        result = {"status": "ok", "data": "test"}
        
        formatted = handler.format_result(result)
        assert "JSON Response" in formatted
        assert json.dumps(result, indent=2) in formatted 