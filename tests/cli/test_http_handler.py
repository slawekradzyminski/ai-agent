"""Tests for the HTTP handler."""
import pytest
from unittest.mock import AsyncMock, Mock
from src.cli.handlers.http import HttpHandler

class TestHttpHandler:
    """Tests for the HttpHandler class."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = Mock()
        agent.make_http_request = AsyncMock()
        return agent
    
    def test_can_handle(self):
        """Test command recognition."""
        handler = HttpHandler(Mock())
        assert handler.can_handle("http: example.com")
        assert handler.can_handle("HTTP: example.com")
        assert not handler.can_handle("search: example.com")
    
    @pytest.mark.asyncio
    async def test_handle(self, mock_agent):
        """Test HTTP command handling."""
        mock_response = {"status": "ok", "data": "test"}
        mock_agent.make_http_request.return_value = mock_response
        
        handler = HttpHandler(mock_agent)
        result = await handler.handle("http: example.com")
        assert result == mock_response
        mock_agent.make_http_request.assert_called_once_with("example.com")
    
    def test_format_result(self, mock_agent):
        """Test result formatting."""
        handler = HttpHandler(mock_agent)
        
        # Test error response
        error_result = {"error": "Failed"}
        formatted = handler.format_result(error_result)
        assert "Error" in formatted
        
        # Test JSON response
        json_result = {"data": {"key": "value"}}
        formatted = handler.format_result(json_result)
        assert "JSON Response" in formatted
        assert "key" in formatted
        
        # Test detailed response
        detailed_result = {
            "status_code": 200,
            "content_type": "application/json",
            "data": {"test": "value"}
        }
        formatted = handler.format_result(detailed_result)
        assert "Status Code: 200" in formatted
        assert "Content Type: application/json" in formatted
        assert "test" in formatted 