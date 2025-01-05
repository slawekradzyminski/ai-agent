"""Browser tool for web scraping."""
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun, BaseCallbackHandler

logger = logging.getLogger(__name__)

class BrowserTool(BaseTool):
    """Tool for browsing web pages using Selenium."""
    
    name: str = Field(default="browser", description="The name of the tool")
    description: str = Field(default="Browse a webpage and extract its content", description="The description of the tool")
    driver: Optional[webdriver.Chrome] = None
    test_mode: bool = Field(default=False, description="Whether to run in test mode")
    logger: logging.Logger = Field(default_factory=lambda: logging.getLogger(__name__))
    callbacks: Optional[List[BaseCallbackHandler]] = Field(default=None, description="Callbacks for the tool")

    def __init__(self, **kwargs):
        """Initialize the browser tool."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing BrowserTool")

    def set_mock_driver(self, mock_driver):
        """Set a mock driver for testing."""
        self.driver = mock_driver

    def get_page_content(self, url: str) -> Dict[str, Any]:
        """Get the content of a webpage."""
        if not url:
            self.logger.error("URL is empty")
            return {"error": "URL cannot be empty"}

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url.lstrip('/')

        if not self.test_mode:
            try:
                # Set up Chrome options
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")  # Updated headless argument
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--remote-debugging-port=9222")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                # Create a new Chrome driver
                self.driver = webdriver.Chrome(options=chrome_options)
                
                # Load the page
                self.driver.get(url)
                
                # Wait for page load
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                except TimeoutException:
                    self.logger.warning("Page load timeout")
                    return {"error": "Page load timeout"}
                
                # Get the page content
                content = self._parse_html_content(self.driver.page_source)
                
                return {"url": url, "content": content}
                
            except WebDriverException as e:
                self.logger.error(f"Browser error: {str(e)}")
                return {"error": f"Browser error: {str(e)}"}
                
            finally:
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception as e:
                        self.logger.error(f"Error closing browser: {str(e)}")
        else:
            # Test mode - return mock content
            return {"url": url, "content": self.driver.page_source if self.driver else ""}

    def _parse_html_content(self, html: str) -> str:
        """Parse HTML content and extract relevant text."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "menu", "footer", "header"]):
            script.decompose()
            
        # Try to find main content
        content = ""
        
        # First try article tag
        article = soup.find('article')
        if article:
            content = article.get_text()
        
        # Then try main tag
        if not content:
            main = soup.find('main')
            if main:
                content = main.get_text()
        
        # Fallback to body content, but try to find the main content div
        if not content:
            # Look for content divs
            content_divs = soup.find_all('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
            if content_divs:
                content = max(content_divs, key=lambda x: len(x.get_text())).get_text()
            else:
                # Last resort: get all text but filter out common navigation elements
                for element in soup.find_all(['div', 'section']):
                    if element.get('class'):
                        classes = ' '.join(element.get('class')).lower()
                        if any(x in classes for x in ['nav', 'menu', 'footer', 'header', 'sidebar']):
                            element.decompose()
                content = soup.get_text()
            
        # Clean up whitespace
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        return content

    async def _arun(
        self,
        url: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Run the browser tool asynchronously."""
        try:
            result = self.get_page_content(url)
            if run_manager:
                try:
                    # Convert result to a string representation for the callback
                    output = result.get("content", "") if "content" in result else str(result.get("error", ""))
                    await run_manager.on_tool_end(
                        output=output,
                        tool_input=url,
                        tool_name=self.name
                    )
                except Exception as e:
                    self.logger.error(f"Error in callback: {str(e)}")
                    # Continue even if callback fails
            return result
        except Exception as e:
            self.logger.error(f"Error in _arun: {str(e)}")
            return {"error": str(e)}

    def _run(self, url: str) -> Dict[str, Any]:
        """Run the browser tool synchronously."""
        raise NotImplementedError("Use _arun instead") 