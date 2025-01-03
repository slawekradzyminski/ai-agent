"""Browser tool for fetching web page content."""
import logging
import json
import traceback
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

    def __init__(self):
        """Initialize the browser tool."""
        logger.info("Initializing BrowserTool")

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
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = None
        try:
            # Initialize the driver
            driver = webdriver.Chrome(options=chrome_options)
            
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
                    'options': chrome_options.arguments
                }
            }
            request_logger.handle(init_record)
            
            # Get the page
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
            if driver:
                try:
                    driver.quit()
                    request_logger.debug(
                        "Browser session cleanup",
                        extra={
                            'cleanup': {
                                'status': 'success',
                                'url': url
                            }
                        }
                    )
                except Exception as e:
                    request_logger.error(
                        "Browser cleanup failed",
                        extra={
                            'cleanup_error': {
                                'url': url,
                                'error': str(e)
                            }
                        }
                    ) 