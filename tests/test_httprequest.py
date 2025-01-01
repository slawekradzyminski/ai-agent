"""Tests for the HTTP request tool."""
import pytest
import responses
from requests.exceptions import RequestException
from src.tools.httprequest import HTTPRequestTool

@pytest.fixture
def http_tool():
    """Create an HTTP request tool instance for testing."""
    return HTTPRequestTool()

@responses.activate
def test_request_success(http_tool):
    """Test successful HTTP request."""
    test_url = "https://test.example.com"
    test_response = {"status": "ok", "data": "test"}
    
    responses.add(
        responses.GET,
        test_url,
        json=test_response,
        status=200
    )
    
    result = http_tool.request(test_url)
    assert result == test_response

@responses.activate
def test_request_error(http_tool):
    """Test handling of request errors."""
    test_url = "https://error.example.com"
    
    responses.add(
        responses.GET,
        test_url,
        body=RequestException("Connection failed")
    )
    
    result = http_tool.request(test_url)
    assert "error" in result
    assert "Connection failed" in result["error"] 