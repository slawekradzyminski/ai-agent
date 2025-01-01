"""Tests for the browser tool."""
import pytest
from unittest.mock import Mock, patch
from selenium.common.exceptions import WebDriverException
from src.tools.browser import BrowserTool

@pytest.fixture
def browser_tool():
    """Create a browser tool instance for testing."""
    return BrowserTool()

@patch('selenium.webdriver.Chrome')
def test_get_page_content_success(mock_chrome, browser_tool):
    """Test successful page content retrieval."""
    # Mock the Chrome driver
    mock_driver = Mock()
    mock_driver.page_source = "<html><body>Test content</body></html>"
    mock_driver.execute_script.return_value = 'complete'
    
    # Mock body element with text
    mock_body = Mock()
    mock_body.text = "Test content"
    mock_driver.find_element.return_value = mock_body
    
    mock_chrome.return_value = mock_driver
    
    # Test content retrieval
    content = browser_tool.get_page_content("https://example.com")
    assert content == "Test content"
    
    # Verify Chrome was initialized with correct options
    mock_chrome.assert_called_once()
    options = mock_chrome.call_args[1]['options']
    assert '--headless' in options.arguments
    assert '--no-sandbox' in options.arguments
    assert '--disable-gpu' in options.arguments
    
    # Verify driver was quit
    mock_driver.quit.assert_called_once()

@patch('selenium.webdriver.Chrome')
def test_get_page_content_error(mock_chrome, browser_tool):
    """Test error handling during page content retrieval."""
    # Mock Chrome driver to raise an exception
    mock_chrome.side_effect = WebDriverException("Chrome error")
    
    # Test error handling
    with pytest.raises(WebDriverException):
        browser_tool.get_page_content("https://example.com") 