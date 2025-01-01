"""DuckDuckGo search tool implementation."""
from typing import Optional, List, Dict, Any
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.callbacks.manager import CallbackManagerForToolRun


class SearchTool:
    """A tool for performing web searches using DuckDuckGo."""

    def __init__(self):
        """Initialize the search tool with DuckDuckGo backend."""
        self.search = DuckDuckGoSearchResults(backend="news")

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
            raw_results = self.search.invoke(query)
            # Parse the raw results string into a list of dictionaries
            results = []
            for result in raw_results.split('\n'):
                if result.strip():
                    # Extract title, link, and snippet using string manipulation
                    parts = result.split(', ')
                    result_dict = {}
                    for part in parts:
                        if ': ' in part:
                            key, value = part.split(': ', 1)
                            result_dict[key.strip()] = value.strip()
                    if result_dict:
                        results.append(result_dict)
            return results
        except Exception as e:
            print(f"Error performing search: {str(e)}")
            return [] 