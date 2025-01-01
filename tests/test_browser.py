"""Tests for the browser tool."""
import pytest
from unittest.mock import Mock, patch
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    mock_driver.quit = Mock()
    
    # Mock WebDriverWait
    mock_wait = Mock(spec=WebDriverWait)
    mock_wait.until.return_value = True
    
    with patch('src.tools.browser.WebDriverWait', return_value=mock_wait):
        mock_chrome.return_value = mock_driver
        
        # Test content retrieval
        content = browser_tool.get_page_content("https://example.com")
        assert content == "Test content"
        
        # Verify driver was quit
        mock_driver.quit.assert_called_once()

@patch('selenium.webdriver.Chrome')
def test_get_page_content_error(mock_chrome, browser_tool):
    """Test error handling during page content retrieval."""
    # Mock Chrome driver to raise an exception
    mock_chrome.return_value = Mock()
    mock_chrome.return_value.get.side_effect = WebDriverException("Chrome error")
    
    # Test error handling
    content = browser_tool.get_page_content("https://example.com")
    assert content == "" 