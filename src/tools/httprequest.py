"""HTTP request tool for making web requests."""
import logging
import requests
from typing import Dict, Any
from src.config.logging_config import request_logger

logger = logging.getLogger(__name__)

class HTTPRequestTool:
    """Tool for making HTTP requests."""

    def __init__(self):
        """Initialize the HTTP request tool."""
        logger.info("Initializing HTTPRequestTool")

    def request(self, url: str) -> Dict[str, Any]:
        """
        Make an HTTP request to a URL.

        Args:
            url: The URL to request

        Returns:
            Dictionary containing the response data or error
        """
        logger.info(f"Making GET request to URL: {url}")
        
        try:
            response = requests.get(url)
            response_data = response.json()
            
            # Log the request and response
            request_logger.info(
                "HTTP Request",
                extra={
                    'request': f"GET {url}",
                    'response': f"Status: {response.status_code}, Body: {response_data}"
                }
            )
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request: {str(e)}"
            logger.error(error_msg)
            
            # Log the error
            request_logger.error(
                "HTTP Request Failed",
                extra={
                    'request': f"GET {url}",
                    'response': f"Error: {str(e)}"
                }
            )
            
            return {"error": error_msg}
        except ValueError as e:
            error_msg = f"Error parsing JSON response: {str(e)}"
            logger.error(error_msg)
            
            # Log the error
            request_logger.error(
                "HTTP Response Parsing Failed",
                extra={
                    'request': f"GET {url}",
                    'response': f"Error parsing JSON: {str(e)}"
                }
            )
            
            return {"error": error_msg} 