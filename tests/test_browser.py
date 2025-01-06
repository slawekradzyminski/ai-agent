import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import WebDriverException, TimeoutException
from src.tools.browser import BrowserTool

@pytest.fixture
def browser_tool():
    return BrowserTool(test_mode=True)

@pytest.fixture(autouse=True)
def mock_selenium(browser_tool):
    mock_options = MagicMock()
    mock_driver = MagicMock()
    mock_wait = MagicMock()
    
    mock_driver.page_source = '<html><body>Test content</body></html>'
    mock_driver.title = 'Test Page'
    mock_driver.current_url = 'http://test.com'
    
    browser_tool.set_mock_driver(mock_driver)
    
    yield {
        'options': mock_options,
        'driver': mock_driver,
        'wait': mock_wait
    }

def test_get_page_content_success(browser_tool, mock_selenium):
    mock_selenium['driver'].page_source = '<html><body><div class="content">Test content</div></body></html>'
    mock_selenium['driver'].execute_script.return_value = 'complete'
    mock_selenium['driver'].title = 'Test Page'
    
    result = browser_tool.get_page_content('http://test.com')
    
    assert 'Test content' in result['content']
    assert result['url'] == 'http://test.com'

def test_get_page_content_timeout(browser_tool, mock_selenium):
    mock_selenium['driver'].execute_script.side_effect = TimeoutException('Page load timeout')
    mock_selenium['driver'].page_source = ''
    mock_selenium['driver'].title = 'Test Page'
    
    result = browser_tool.get_page_content('http://test.com')
    
    assert result['content'] == ''
    assert result['url'] == 'http://test.com'

def test_get_page_content_driver_error(browser_tool, mock_selenium):
    mock_selenium['driver'].get.side_effect = WebDriverException('Driver error')
    mock_selenium['driver'].page_source = ''
    
    result = browser_tool.get_page_content('http://test.com')
    
    assert result['content'] == ''
    assert result['url'] == 'http://test.com'

def test_get_page_content_cleanup_on_error(browser_tool, mock_selenium):
    mock_selenium['driver'].get.side_effect = WebDriverException('Page load error')
    mock_selenium['driver'].page_source = ''
    
    result = browser_tool.get_page_content('http://test.com')
    
    assert result['content'] == ''
    assert result['url'] == 'http://test.com'

def test_get_page_content_cleanup_on_quit_error(browser_tool, mock_selenium):
    mock_selenium['driver'].page_source = '<html><body><div class="content">Test content</div></body></html>'
    mock_selenium['driver'].execute_script.return_value = 'complete'
    mock_selenium['driver'].title = 'Test Page'
    mock_selenium['driver'].quit.side_effect = Exception('Quit error')
    
    result = browser_tool.get_page_content('http://test.com')
    
    assert 'Test content' in result['content']
    assert result['url'] == 'http://test.com'

def test_parse_html_content_with_article(browser_tool):
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