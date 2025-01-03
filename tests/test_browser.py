"""Tests for the browser tool."""
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import WebDriverException, TimeoutException
from src.tools.browser import BrowserTool

@pytest.fixture
def browser_tool():
    """Create a browser tool instance for testing."""
    return BrowserTool()

def test_get_page_content_success(browser_tool):
    """Test successful page content retrieval."""
    mock_driver = MagicMock()
    mock_driver.page_source = '<html><body><div class="content">Test content</div></body></html>'
    mock_driver.execute_script.return_value = 'complete'
    
    with patch('selenium.webdriver.Chrome', return_value=mock_driver):
        content = browser_tool.get_page_content('http://test.com')
        
    assert 'Test content' in content
    mock_driver.quit.assert_called_once()

def test_get_page_content_timeout(browser_tool):
    """Test handling of page load timeout."""
    mock_driver = MagicMock()
    mock_driver.execute_script.side_effect = TimeoutException('Page load timeout')
    
    with patch('selenium.webdriver.Chrome', return_value=mock_driver):
        content = browser_tool.get_page_content('http://test.com')
        
    assert content == ''
    mock_driver.quit.assert_called_once()

def test_get_page_content_driver_error(browser_tool):
    """Test error handling in page content retrieval."""
    with patch('selenium.webdriver.Chrome', side_effect=WebDriverException('Driver error')):
        content = browser_tool.get_page_content('http://test.com')
        
    assert content == ''

def test_get_page_content_cleanup_on_error(browser_tool):
    """Test driver cleanup on page load error."""
    mock_driver = MagicMock()
    mock_driver.get.side_effect = WebDriverException('Page load error')
    
    with patch('selenium.webdriver.Chrome', return_value=mock_driver):
        content = browser_tool.get_page_content('http://test.com')
        
    assert content == ''
    mock_driver.quit.assert_called_once()

def test_get_page_content_cleanup_on_quit_error(browser_tool):
    """Test driver cleanup on quit error."""
    mock_driver = MagicMock()
    mock_driver.quit.side_effect = Exception('Quit error')
    
    with patch('selenium.webdriver.Chrome', return_value=mock_driver):
        content = browser_tool.get_page_content('http://test.com')
        
    # Test should complete without raising an exception
    assert True

def test_parse_html_content_with_article(browser_tool):
    """Test HTML parsing with article tag."""
    html = """
    <html>
        <head><script>var x = 1;</script></head>
        <body>
            <nav>Menu</nav>
            <article>
                <h1>Title</h1>
                <p>Important content</p>
            </article>
            <footer>Footer</footer>
        </body>
    </html>
    """
    content = browser_tool._parse_html_content(html)
    assert "Title" in content
    assert "Important content" in content
    assert "Menu" not in content
    assert "Footer" not in content

def test_parse_html_content_with_main(browser_tool):
    """Test HTML parsing with main tag."""
    html = """
    <html>
        <body>
            <nav>Menu</nav>
            <main>
                <div>Main content</div>
            </main>
            <footer>Footer</footer>
        </body>
    </html>
    """
    content = browser_tool._parse_html_content(html)
    assert "Main content" in content
    assert "Menu" not in content
    assert "Footer" not in content

def test_parse_html_content_fallback(browser_tool):
    """Test HTML parsing fallback when no article/main tags."""
    html = """
    <html>
        <body>
            <div class="content">
                <p>Important text</p>
            </div>
            <div class="menu">Menu items</div>
        </body>
    </html>
    """
    content = browser_tool._parse_html_content(html)
    assert "Important text" in content
    assert "Menu items" not in content

def test_get_page_content_timeout(browser_tool):
    """Test handling of page load timeout."""
    mock_driver = MagicMock()
    mock_driver.page_source = "<html><body>Partial content</body></html>"
    mock_driver.execute_script.return_value = "loading"  # Simulate never reaching 'complete'
    
    with patch('selenium.webdriver.Chrome', return_value=mock_driver), \
         patch('selenium.webdriver.support.ui.WebDriverWait.until', side_effect=Exception("Timeout")):
        content = browser_tool.get_page_content("https://example.com")
        assert content == ""
        mock_driver.quit.assert_called_once() 