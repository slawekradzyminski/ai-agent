"""Browser tool for fetching web page content."""
import logging
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
        logger.info(f"Fetching content from URL: {url}")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = None
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
            
            try:
                # Wait for the page to load
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except (TimeoutException, Exception) as e:
                logger.error(f"Page load timeout for {url}: {str(e)}")
                return ""
            
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
            if driver:
                try:
                    driver.quit()
                except:
                    pass 