"""Browser tool for fetching web page content."""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
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
        
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link", "noscript"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text: remove multiple newlines and spaces
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)

    def get_page_content(self, url: str) -> str:
        """
        Fetch content from a URL using Chrome WebDriver.
        
        Args:
            url: The URL to fetch content from.
            
        Returns:
            str: The parsed page content with only meaningful text.
        """
        logger.info(f"Fetching content from URL: {url}")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            # Initialize the driver
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
            
            # Log the page visit
            request_logger.info(
                "Browser Page Visit",
                extra={
                    'request': f"URL: {url}",
                    'response': "Starting page load..."
                }
            )
            
            # Get the page
            driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Get the page source
            page_source = driver.page_source
            
            # Parse and clean the content
            text = self._parse_html_content(page_source)
            
            # Log both raw HTML and cleaned text
            request_logger.info(
                "Browser Content Retrieved",
                extra={
                    'request': f"URL: {url}",
                    'response': (
                        f"Raw HTML length: {len(page_source)}\n"
                        f"Cleaned text length: {len(text)}\n"
                        f"Returned cleaned text:\n{text}"
                    )
                }
            )
            
            logger.info(f"Successfully retrieved content from {url}")
            
            return text
            
        except WebDriverException as e:
            error_msg = f"Error fetching content from {url}: {str(e)}"
            logger.error(error_msg)
            
            # Log the error
            request_logger.error(
                "Browser Page Load Failed",
                extra={
                    'request': f"URL: {url}",
                    'response': f"Error: {str(e)}"
                }
            )
            
            return ""
            
        finally:
            try:
                driver.quit()
            except:
                pass 