"""HTTP request tool for making web requests."""
import logging
import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class HTTPRequestTool:
    """Tool for making HTTP requests to web pages."""

    def __init__(self):
        """Initialize the HTTPRequestTool."""
        logger.info("Initializing HTTPRequestTool")
        self.session = requests.Session()

    def request(self, url: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the specified URL."""
        try:
            logger.info(f"Making {method} request to URL: {url}")
            
            # Create request headers
            request_headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Add custom headers if provided
            if headers:
                request_headers.update(headers)
            
            # Make the request
            response = self.session.request(
                method,
                url,
                headers=request_headers,
                allow_redirects=True,
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise 