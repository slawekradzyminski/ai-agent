"""HTTP request tool for making web requests."""
import logging
import json
import traceback
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
        # Log request initiation
        request_logger.info(f"HTTP Request initiated to: {url}")
        request_logger.debug(
            "Request details",
            extra={
                'request': {
                    'method': 'GET',
                    'url': url,
                    'headers': {'User-Agent': 'AI-Agent/1.0'}
                }
            }
        )
        
        try:
            response = requests.get(url)
            content_type = response.headers.get('content-type', '').lower()
            
            # Extract response data based on content type
            if 'application/json' in content_type:
                response_data = response.json()
                log_content = json.dumps(response_data, indent=2)
            elif 'text/html' in content_type:
                response_data = {
                    'content': response.text,
                    'content_type': 'text/html'
                }
                log_content = response.text
            elif 'text/plain' in content_type:
                response_data = {
                    'content': response.text,
                    'content_type': 'text/plain'
                }
                log_content = response.text
            else:
                response_data = {
                    'content': response.text,
                    'content_type': content_type
                }
                log_content = response.text
            
            # Create record with complete response data
            record = logging.LogRecord(
                name='ai_agent',
                level=logging.DEBUG,
                pathname=__file__,
                lineno=0,
                msg="Complete HTTP Response",
                args=(),
                exc_info=None
            )
            record.extra = {
                'request': {
                    'method': 'GET',
                    'url': url,
                    'headers': dict(response.request.headers)
                },
                'response': {
                    'status_code': response.status_code,
                    'content_type': content_type,
                    'headers': dict(response.headers),
                    'raw_content': response.text,
                    'formatted_content': log_content,
                    'content_length': len(response.text)
                }
            }
            request_logger.handle(record)
            
            # Log summary at info level
            request_logger.info(
                f"HTTP Request completed: status={response.status_code}, "
                f"type={content_type}, length={len(response.text)} chars",
                extra={
                    'summary': {
                        'request_url': url,
                        'status_code': response.status_code,
                        'content_type': content_type,
                        'content_length': len(response.text)
                    }
                }
            )
            
            return {
                'status_code': response.status_code,
                'content_type': content_type,
                'data': response_data
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request: {str(e)}"
            
            # Log complete error details
            request_logger.error(
                "HTTP Request Failed",
                extra={
                    'error_details': {
                        'request': {
                            'method': 'GET',
                            'url': url,
                            'headers': {'User-Agent': 'AI-Agent/1.0'}
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
            
            return {"error": error_msg}
        except ValueError as e:
            error_msg = f"Error parsing response: {str(e)}"
            
            # Log complete parsing error details
            request_logger.error(
                "HTTP Response Parsing Failed",
                extra={
                    'error_details': {
                        'request': {
                            'method': 'GET',
                            'url': url,
                            'headers': {'User-Agent': 'AI-Agent/1.0'}
                        },
                        'error': {
                            'type': 'ValueError',
                            'message': str(e),
                            'details': repr(e),
                            'traceback': traceback.format_exc()
                        }
                    }
                }
            )
            
            return {"error": error_msg} 