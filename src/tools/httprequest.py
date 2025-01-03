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
            content_type = response.headers.get('content-type', '').lower()
            
            # Extract response data based on content type
            if 'application/json' in content_type:
                response_data = response.json()
            elif 'text/html' in content_type:
                response_data = {
                    'content': response.text,
                    'content_type': 'text/html'
                }
            elif 'text/plain' in content_type:
                response_data = {
                    'content': response.text,
                    'content_type': 'text/plain'
                }
            else:
                # Default to treating as text
                response_data = {
                    'content': response.text,
                    'content_type': content_type
                }
            
            # Log the request and response
            request_logger.info(
                "HTTP Request",
                extra={
                    'request': f"GET {url}",
                    'response': f"Status: {response.status_code}, Content-Type: {content_type}"
                }
            )
            
            return {
                'status_code': response.status_code,
                'content_type': content_type,
                'data': response_data
            }
            
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
            error_msg = f"Error parsing response: {str(e)}"
            logger.error(error_msg)
            
            # Log the error
            request_logger.error(
                "HTTP Response Parsing Failed",
                extra={
                    'request': f"GET {url}",
                    'response': f"Error parsing response: {str(e)}"
                }
            )
            
            return {"error": error_msg} 