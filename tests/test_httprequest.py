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
def test_request_json_response(http_tool):
    """Test successful HTTP request with JSON response."""
    test_url = "https://test.example.com"
    test_response = {"status": "ok", "data": "test"}
    
    responses.add(
        responses.GET,
        test_url,
        json=test_response,
        status=200,
        content_type='application/json'
    )
    
    result = http_tool.request(test_url)
    assert result['status_code'] == 200
    assert 'application/json' in result['content_type']
    assert result['data'] == test_response

@responses.activate
def test_request_html_response(http_tool):
    """Test successful HTTP request with HTML response."""
    test_url = "https://test.example.com"
    test_html = "<html><body>Test content</body></html>"
    
    responses.add(
        responses.GET,
        test_url,
        body=test_html,
        status=200,
        content_type='text/html'
    )
    
    result = http_tool.request(test_url)
    assert result['status_code'] == 200
    assert 'text/html' in result['content_type']
    assert result['data']['content'] == test_html
    assert result['data']['content_type'] == 'text/html'

@responses.activate
def test_request_text_response(http_tool):
    """Test successful HTTP request with plain text response."""
    test_url = "https://test.example.com"
    test_text = "Plain text content"
    
    responses.add(
        responses.GET,
        test_url,
        body=test_text,
        status=200,
        content_type='text/plain'
    )
    
    result = http_tool.request(test_url)
    assert result['status_code'] == 200
    assert 'text/plain' in result['content_type']
    assert result['data']['content'] == test_text
    assert result['data']['content_type'] == 'text/plain'

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

@responses.activate
def test_request_unknown_content_type(http_tool):
    """Test handling of unknown content type."""
    test_url = "https://test.example.com"
    test_content = "Some binary data"
    
    responses.add(
        responses.GET,
        test_url,
        body=test_content,
        status=200,
        content_type='application/octet-stream'
    )
    
    result = http_tool.request(test_url)
    assert result['status_code'] == 200
    assert 'application/octet-stream' in result['content_type']
    assert result['data']['content'] == test_content
    assert result['data']['content_type'] == 'application/octet-stream' 