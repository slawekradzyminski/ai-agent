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
        """Make an HTTP request to the specified URL.

        Args:
            url: The URL to request.
            method: The HTTP method to use (default: GET).
            headers: Optional headers to include in the request.

        Returns:
            Dict containing the response data.

        Raises:
            RequestException: If the request fails.
        """
        try:
            logger.info(f"Making {method} request to URL: {url}")
            response = self.session.request(method, url, headers=headers)
            response.raise_for_status()

            # Try to parse as JSON first
            try:
                return response.json()
            except ValueError:
                # If not JSON, return text content
                return {
                    "content": response.text,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }

        except RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise 