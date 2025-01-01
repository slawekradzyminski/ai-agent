"""Tests for the HTTP request tool."""
import pytest
import responses
from requests.exceptions import RequestException
from src.tools.httprequest import HTTPRequestTool

@pytest.fixture
def http_tool():
    """Create an instance of HTTPRequestTool for testing."""
    return HTTPRequestTool()

@responses.activate
def test_request_json(http_tool):
    """Test making a request that returns JSON."""
    test_url = "https://api.example.com/data"
    test_data = {"key": "value"}
    
    responses.add(
        responses.GET,
        test_url,
        json=test_data,
        status=200
    )
    
    result = http_tool.request(test_url)
    assert result == test_data

@responses.activate
def test_request_text(http_tool):
    """Test making a request that returns text."""
    test_url = "https://example.com"
    test_content = "<html><body>Test content</body></html>"
    
    responses.add(
        responses.GET,
        test_url,
        body=test_content,
        status=200
    )
    
    result = http_tool.request(test_url)
    assert result["content"] == test_content
    assert result["status_code"] == 200
    assert "headers" in result

@responses.activate
def test_request_error(http_tool):
    """Test handling of request errors."""
    test_url = "https://error.example.com"
    
    responses.add(
        responses.GET,
        test_url,
        status=404
    )
    
    with pytest.raises(RequestException):
        http_tool.request(test_url) 