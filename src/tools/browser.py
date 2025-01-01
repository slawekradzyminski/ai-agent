"""Browser tool for web scraping using Selenium."""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException

logger = logging.getLogger(__name__)

class BrowserTool:
    """Tool for browser automation using Selenium."""

    def __init__(self):
        """Initialize the BrowserTool with Chrome WebDriver."""
        logger.info("Initializing BrowserTool")
        self.driver = None

    def _setup_driver(self):
        """Set up Chrome WebDriver with appropriate options."""
        if self.driver is None:
            options = Options()
            options.add_argument('--headless')  # Run in headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            try:
                self.driver = webdriver.Chrome(options=options)
                logger.info("Chrome WebDriver initialized successfully")
            except WebDriverException as e:
                logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
                raise

    def get_page_content(self, url: str, wait_time: int = 10) -> str:
        """
        Open a URL in Chrome and return the page content.

        Args:
            url: The URL to open
            wait_time: Maximum time to wait for page load in seconds

        Returns:
            The page content as a string
        """
        try:
            logger.info(f"Fetching content from URL: {url}")
            self._setup_driver()
            
            # Load the page
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, wait_time).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Wait for any dynamic content to load
            try:
                # Wait for body to contain text
                WebDriverWait(self.driver, wait_time).until(
                    lambda d: len(d.find_element(By.TAG_NAME, "body").text) > 0
                )
                
                # Additional wait for any JavaScript frameworks to initialize
                self.driver.execute_script("return new Promise(resolve => setTimeout(resolve, 1000))")
            except TimeoutException:
                logger.warning("Timeout waiting for dynamic content")
            
            # Get page content
            content = self.driver.page_source
            text_content = self.driver.find_element(By.TAG_NAME, "body").text
            
            logger.info(f"Successfully retrieved content from {url}")
            return text_content

        except WebDriverException as e:
            logger.error(f"Error accessing {url}: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None 