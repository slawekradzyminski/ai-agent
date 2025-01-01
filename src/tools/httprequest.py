"""HTTP request tool for making web requests."""
import logging
import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import html2text
import random

logger = logging.getLogger(__name__)

class HTTPRequestTool:
    """Tool for making HTTP requests to web pages."""

    def __init__(self):
        """Initialize the HTTPRequestTool."""
        logger.info("Initializing HTTPRequestTool")
        self.session = requests.Session()
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
        # List of common user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]

    def request(self, url: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the specified URL."""
        try:
            logger.info(f"Making {method} request to URL: {url}")
            
            # Create request headers
            request_headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
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

            content_type = response.headers.get('content-type', '').lower()
            
            # Handle different content types
            if 'application/json' in content_type:
                return self._handle_json_response(response)
            elif 'text/html' in content_type:
                return self._handle_html_response(response)
            else:
                return self._handle_text_response(response)

        except RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise

    def _handle_html_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTML response by parsing and extracting content."""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript', 'iframe']):
            element.decompose()
        
        # Extract title
        title = soup.title.string if soup.title else None
        
        # Extract meta description
        meta_desc = None
        for meta_name in ['description', 'og:description']:
            meta_tag = soup.find('meta', attrs={'name': meta_name}) or soup.find('meta', attrs={'property': f'og:{meta_name}'})
            if meta_tag:
                meta_desc = meta_tag.get('content')
                break
        
        # Try to find the main content
        content_selectors = [
            '#productTitle',  # Amazon product title
            '#bookDescription_feature_div',  # Amazon book description
            '#detailBullets_feature_div',  # Amazon product details
            '#dp-container',  # Amazon product container
            '#centerCol',  # Amazon center column
            'main',
            'article',
            '#content',
            '.content',
            '#main-content',
            '.main-content'
        ]
        
        content_parts = []
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content_parts.append(self.html_converter.handle(str(element)))
        
        if content_parts:
            content = '\n\n'.join(content_parts)
        else:
            # Fallback to body content
            body = soup.find('body')
            if body:
                content = self.html_converter.handle(str(body))
            else:
                content = self.html_converter.handle(str(soup))
        
        return {
            'url': response.url,
            'title': title,
            'description': meta_desc,
            'content': content,
            'status_code': response.status_code,
            'content_type': 'html',
            'headers': dict(response.headers)
        }

    def _handle_json_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle JSON response."""
        return {
            'url': response.url,
            'content': response.json(),
            'status_code': response.status_code,
            'content_type': 'json',
            'headers': dict(response.headers)
        }

    def _handle_text_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle plain text response."""
        return {
            'url': response.url,
            'content': response.text,
            'status_code': response.status_code,
            'content_type': 'text',
            'headers': dict(response.headers)
        } 