import pytest
import aiohttp
from aioresponses import aioresponses
from src.tools.http import HttpTool

@pytest.fixture
def http_tool():
    return HttpTool()

@pytest.mark.asyncio
async def test_request_json_response(http_tool):
    test_url = "https://test.example.com"
    test_response = {"status": "ok", "data": "test"}
    
    with aioresponses() as m:
        m.get(test_url, status=200, payload=test_response)
        response = await http_tool._arun(test_url)
        assert response == test_response

@pytest.mark.asyncio
async def test_request_html_response(http_tool):
    test_url = "https://test.example.com"
    test_html = "<html><body>Test content</body></html>"
    
    with aioresponses() as m:
        m.get(test_url, status=200, body=test_html, headers={'Content-Type': 'text/html'})
        response = await http_tool._arun(test_url)
        assert response == test_html

@pytest.mark.asyncio
async def test_request_text_response(http_tool):
    test_url = "https://test.example.com"
    test_text = "Plain text content"
    
    with aioresponses() as m:
        m.get(test_url, status=200, body=test_text, headers={'Content-Type': 'text/plain'})
        response = await http_tool._arun(test_url)
        assert response == test_text

@pytest.mark.asyncio
async def test_request_error(http_tool):
    test_url = "https://error.example.com"
    
    with aioresponses() as m:
        m.get(test_url, exception=aiohttp.ClientError())
        response = await http_tool._arun(test_url)
        assert isinstance(response, dict)
        assert "error" in response 