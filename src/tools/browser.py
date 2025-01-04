"""Browser tool for fetching web page content."""
import logging
import json
import traceback
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
from src.config.logging_config import request_logger

logger = logging.getLogger(__name__)

class BrowserTool:
    """Tool for fetching web page content using Selenium."""

    def __init__(self, test_mode=False):
        """Initialize the browser tool."""
        logger.info("Initializing BrowserTool")
        self.test_mode = test_mode or os.getenv('PYTEST_CURRENT_TEST') is not None
        self.mock_driver = None

    def set_mock_driver(self, mock_driver):
        """Set a mock driver for testing."""
        self.mock_driver = mock_driver

    def _get_driver(self):
        """Get a WebDriver instance, using mock in test mode."""
        if self.test_mode:
            if self.mock_driver is None:
                # Create a basic mock if none provided
                from unittest.mock import Mock
                mock_driver = Mock()
                mock_driver.page_source = "<html><body>Test content</body></html>"
                mock_driver.title = "Test Page"
                mock_driver.current_url = "http://test.com"
                self.mock_driver = mock_driver
            return self.mock_driver
        
        # Set up Chrome options for real browser
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=chrome_options)

    def _parse_html_content(self, html: str) -> str:
        """
        Parse HTML content and extract meaningful text.
        
        Args:
            html: Raw HTML content to parse.
            
        Returns:
            str: Cleaned and formatted text content.
        """
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for element in soup(["script", "style", "meta", "link", "noscript", "header", "footer", "nav"]):
            element.decompose()
        
        # Try to find the main content area using common patterns
        main_content = None
        
        # Look for article or main content by common class/id patterns
        content_indicators = [
            # Classes
            {"class_": ["article", "post", "content", "main-content", "entry-content", "post-content"]},
            # IDs
            {"id": ["article", "post", "content", "main-content", "entry-content", "post-content"]},
            # Tags
            {"name": ["article", "main"]}
        ]
        
        for indicator in content_indicators:
            found = soup.find(**indicator)
            if found:
                main_content = found
                break
        
        # If we found a main content area, use that
        if main_content:
            # Remove any remaining navigation/menu elements within the main content
            for nav in main_content.find_all(class_=lambda x: x and any(term in str(x).lower() for term in ["menu", "nav", "sidebar", "footer"])):
                nav.decompose()
            
            # Get text from main content
            text = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback: use the whole body but try to clean it up
            body = soup.find('body')
            if body:
                # Remove elements likely to be navigation/menus/footers
                for element in body.find_all(class_=lambda x: x and any(term in str(x).lower() for term in ["menu", "nav", "sidebar", "footer", "header"])):
                    element.decompose()
                text = body.get_text(separator='\n', strip=True)
            else:
                # Last resort: just get all text
                text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text
        lines = []
        for line in text.splitlines():
            line = line.strip()
            # Skip empty lines and very short lines that are likely menu items
            if line and len(line) > 3:
                # Skip lines that look like navigation (short text with special characters)
                if not (len(line) < 20 and any(char in line for char in ['»', '›', '|', '•', '>', '<'])):
                    lines.append(line)
        
        # Join lines, but add extra newline between paragraphs
        text = '\n'.join(lines)
        
        # Remove redundant whitespace while preserving paragraph breaks
        text = '\n'.join(line for line in text.splitlines() if line.strip())
        
        return text

    def get_page_content(self, url: str) -> str:
        """
        Fetch content from a URL using Chrome WebDriver.
        
        Args:
            url: The URL to fetch content from.
            
        Returns:
            str: The parsed page content with only meaningful text.
        """
        # Log request initiation
        request_logger.info(f"Browser request initiated to: {url}")
        request_logger.debug(
            "Browser request details",
            extra={
                'request': {
                    'method': 'GET',
                    'url': url,
                    'tool': 'BrowserTool',
                    'options': {
                        'headless': True,
                        'no-sandbox': True,
                        'disable-dev-shm-usage': True
                    }
                }
            }
        )
        
        driver = None
        try:
            # Get the appropriate driver
            driver = self._get_driver()
            
            # Create initialization record
            init_record = logging.LogRecord(
                name='ai_agent',
                level=logging.DEBUG,
                pathname=__file__,
                lineno=0,
                msg="Chrome WebDriver initialized",
                args=(),
                exc_info=None
            )
            init_record.extra = {
                'browser_init': {
                    'status': 'success',
                    'options': ['--headless', '--no-sandbox', '--disable-dev-shm-usage'] if not self.test_mode else ['test_mode']
                }
            }
            request_logger.handle(init_record)
            
            # Get the page
            if not self.test_mode:
                driver.get(url)
                
                try:
                    # Wait for the page to load
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                except (TimeoutException, Exception) as e:
                    error_msg = f"Page load timeout for {url}: {str(e)}"
                    request_logger.error(
                        "Browser Page Load Timeout",
                        extra={
                            'error_details': {
                                'request': {
                                    'url': url,
                                    'tool': 'BrowserTool'
                                },
                                'error': {
                                    'type': type(e).__name__,
                                    'message': str(e),
                                    'details': repr(e),
                                    'traceback': traceback.format_exc()
                                }
                            }
                        }
                    )
                    return ""

            # Get the page source
            page_source = driver.page_source
            
            # Parse and clean the content
            text = self._parse_html_content(page_source)
            
            # Create complete response record
            response_record = logging.LogRecord(
                name='ai_agent',
                level=logging.DEBUG,
                pathname=__file__,
                lineno=0,
                msg="Complete Browser Response",
                args=(),
                exc_info=None
            )
            response_record.extra = {
                'request': {
                    'method': 'GET',
                    'url': url,
                    'tool': 'BrowserTool'
                },
                'response': {
                    'page_title': driver.title,
                    'current_url': driver.current_url,
                    'raw_html_length': len(page_source),
                    'cleaned_text_length': len(text),
                    'raw_html': page_source[:1000] + '...' if len(page_source) > 1000 else page_source,
                    'cleaned_text': text
                }
            }
            request_logger.handle(response_record)
            
            # Log summary at info level
            request_logger.info(
                f"Browser request completed: title='{driver.title}', "
                f"content_length={len(text)} chars",
                extra={
                    'summary': {
                        'request_url': url,
                        'final_url': driver.current_url,
                        'page_title': driver.title,
                        'content_length': len(text)
                    }
                }
            )
            
            return text
            
        except WebDriverException as e:
            error_msg = f"Error fetching content from {url}: {str(e)}"
            
            # Log complete error details
            request_logger.error(
                "Browser Request Failed",
                extra={
                    'error_details': {
                        'request': {
                            'url': url,
                            'tool': 'BrowserTool'
                        },
                        'error': {
                            'type': type(e).__name__,
                            'message': str(e),
                            'details': repr(e),
                            'traceback': traceback.format_exc()
                        }
                    }
                }
            )
            return ""
            
        finally:
            if driver and not self.test_mode:
                try:
                    driver.quit()
                except Exception as e:
                    request_logger.error(
                        "Browser cleanup failed",
                        extra={
                            'error_details': {
                                'error': {
                                    'type': type(e).__name__,
                                    'message': str(e),
                                    'details': repr(e),
                                    'traceback': traceback.format_exc()
                                }
                            }
                        }
                    )
                request_logger.debug("Browser session cleanup") 