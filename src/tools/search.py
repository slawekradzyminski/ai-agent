"""DuckDuckGo search tool implementation."""
import logging
from typing import Optional, List, Dict, Any
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.callbacks.manager import CallbackManagerForToolRun
from src.config.settings import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SearchTool:
    """A tool for performing web searches using DuckDuckGo."""

    def __init__(self):
        """Initialize the search tool with DuckDuckGo backend."""
        logger.info("Initializing SearchTool with DuckDuckGo backends")
        self.text_search = DuckDuckGoSearchResults(backend="text")

    def search_web(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search using DuckDuckGo.

        Args:
            query: The search query string
            run_manager: Optional callback manager for the tool run

        Returns:
            List of search results as dictionaries
        """
        try:
            logger.info(f"Performing web search for query: {query}")
            
            # Perform text search
            logger.debug("Attempting text search")
            results = self.text_search.invoke(query)
            logger.debug(f"Raw results: {results}")

            # Parse results
            all_results = []
            
            if results:
                # Split the results string into individual result entries
                entries = []
                current_entry = {}
                
                # Parse the comma-separated key-value pairs
                for part in results.split(', '):
                    if ': ' in part:
                        key, value = part.split(': ', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'title' and current_entry:
                            # Start of a new entry
                            entries.append(current_entry)
                            current_entry = {}
                        
                        current_entry[key] = value
                
                # Add the last entry
                if current_entry:
                    entries.append(current_entry)
                
                # Convert entries to our standard format
                for entry in entries:
                    if 'title' in entry and 'link' in entry:
                        result = {
                            'title': entry['title'],
                            'link': entry['link'],
                            'source': 'text'
                        }
                        if 'snippet' in entry:
                            result['snippet'] = entry['snippet']
                        all_results.append(result)
            
            logger.info(f"Found {len(all_results)} results")
            logger.debug(f"Search results: {all_results}")
            return all_results
            
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}", exc_info=True)
            return [] 