"""Search tool implementation using DuckDuckGo."""
import logging
from typing import List, Dict, Any
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from src.config.logging_config import request_logger

logger = logging.getLogger(__name__)

class SearchTool:
    """Tool for performing web searches using DuckDuckGo."""

    def __init__(self):
        """Initialize the search tool with DuckDuckGo backend."""
        logger.info("Initializing SearchTool with DuckDuckGo backends")
        self.search = DuckDuckGoSearchAPIWrapper()

    def search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a web search using DuckDuckGo.

        Args:
            query: Search query string

        Returns:
            List of search results
        """
        logger.info(f"Performing web search for query: {query}")
        
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
            
            # Log the request and response
            request_logger.info(
                "DuckDuckGo Search",
                extra={
                    'request': f"Query: {query}",
                    'response': f"Found {len(results)} results: {results}"
                }
            )
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            error_msg = f"Error performing search: {str(e)}"
            logger.error(error_msg)
            
            # Log the error
            request_logger.error(
                "DuckDuckGo Search Failed",
                extra={
                    'request': f"Query: {query}",
                    'response': f"Error: {str(e)}"
                }
            )
            
            return [] 