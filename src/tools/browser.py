"""Browser tool for fetching web content."""
import logging
from typing import Optional, Dict, Any, Literal
from pydantic import Field
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)

class BrowserTool(BaseTool):
    """Tool for browsing web pages using Selenium."""
    
    name: Literal["browser"] = Field(default="browser")
    description: Literal["Browse web pages and extract their content"] = Field(default="Browse web pages and extract their content")
    logger: logging.Logger = Field(default_factory=lambda: logging.getLogger(__name__))
    mock_driver: Optional[Any] = Field(default=None, exclude=True)

    def __init__(self, **kwargs):
        """Initialize the browser tool."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing BrowserTool")

    def set_mock_driver(self, mock_driver):
        """Set a mock driver for testing."""
        self.mock_driver = mock_driver

    def _parse_html_content(self, html: str) -> str:
        """Parse HTML content and extract relevant text."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "menu"]):
            script.decompose()
        
        # Try to find the main content
        main_content = None
        
        # Look for article or main tags first
        if soup.find('article'):
            main_content = soup.find('article')
        elif soup.find('main'):
            main_content = soup.find('main')
        else:
            # Look for the largest content div
            content_divs = soup.find_all('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
            if content_divs:
                main_content = max(content_divs, key=lambda x: len(x.get_text()))
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.body
        
        # Get text and clean it up
        text = main_content.get_text(separator=' ', strip=True)
        return text

    def get_page_content(self, url: str) -> str:
        """Get the content of a web page."""
        driver = None
        try:
            if self.mock_driver:
                driver = self.mock_driver
            else:
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(options=options)

            driver.get(url)
            wait = WebDriverWait(driver, 10)
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            
            content = self._parse_html_content(driver.page_source)
            return content

        except TimeoutException as e:
            self.logger.error(f"Timeout while loading page {url}: {str(e)}")
            return ""
        except WebDriverException as e:
            self.logger.error(f"WebDriver error for {url}: {str(e)}")
            return ""
        except Exception as e:
            self.logger.error(f"Error getting content from {url}: {str(e)}")
            return ""
        finally:
            if driver and not self.mock_driver:
                try:
                    driver.quit()
                except Exception as e:
                    self.logger.error(f"Error closing browser: {str(e)}")

    async def _arun(self, url: str) -> Dict[str, Any]:
        """Run the browser tool asynchronously."""
        content = self.get_page_content(url)
        return {"url": url, "content": content}

    def _run(self, url: str) -> Dict[str, Any]:
        """Run the browser tool synchronously."""
        return {"url": url, "content": self.get_page_content(url)} 