"""Search tool implementation using DuckDuckGo."""
import logging
import json
import traceback
from typing import List, Dict, Any
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from src.config.logging_config import request_logger

logger = logging.getLogger(__name__)

class SearchTool:
    """Tool for performing web searches using DuckDuckGo."""

    def __init__(self):
        """Initialize the search tool with DuckDuckGo backend."""
        logger.info("Initializing SearchTool with DuckDuckGo backend")
        self.search = DuckDuckGoSearchAPIWrapper()

    def search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a web search using DuckDuckGo.

        Args:
            query: Search query string

        Returns:
            List of search results
        """
        # Log search initiation
        request_logger.info(f"Search request initiated with query: {query}")
        request_logger.debug(
            "Search request details",
            extra={
                'request': {
                    'tool': 'SearchTool',
                    'engine': 'DuckDuckGo',
                    'query': query,
                    'max_results': 4
                }
            }
        )
        
        try:
            # Get raw results
            raw_results = self.search.results(query, max_results=4)
            
            # Format results
            results = [
                {
                    "title": result.get("title", "No title"),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "No snippet available"),
                    "source": "DuckDuckGo"
                }
                for result in raw_results
            ]
            
            # Create complete response record
            response_record = logging.LogRecord(
                name='ai_agent',
                level=logging.DEBUG,
                pathname=__file__,
                lineno=0,
                msg="Complete Search Response",
                args=(),
                exc_info=None
            )
            response_record.extra = {
                'request': {
                    'tool': 'SearchTool',
                    'engine': 'DuckDuckGo',
                    'query': query
                },
                'response': {
                    'result_count': len(results),
                    'raw_results': raw_results,
                    'formatted_results': results
                }
            }
            request_logger.handle(response_record)
            
            # Log summary at info level
            request_logger.info(
                f"Search completed: found {len(results)} results",
                extra={
                    'summary': {
                        'query': query,
                        'result_count': len(results),
                        'result_urls': [r['link'] for r in results]
                    }
                }
            )
            
            return results
            
        except Exception as e:
            error_msg = f"Error performing search: {str(e)}"
            
            # Log complete error details
            request_logger.error(
                "Search Request Failed",
                extra={
                    'error_details': {
                        'request': {
                            'tool': 'SearchTool',
                            'engine': 'DuckDuckGo',
                            'query': query
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
            
            return [] 