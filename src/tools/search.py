"""Search tool for performing web searches."""
import logging
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS
from langchain.tools import BaseTool

class SearchTool(BaseTool):
    """Tool for performing web searches using DuckDuckGo."""
    
    name: Literal["search"] = Field(default="search")
    description: Literal["Search the web for information about a topic"] = Field(default="Search the web for information about a topic")
    ddgs: Optional[DDGS] = Field(default_factory=DDGS)
    logger: logging.Logger = Field(default_factory=lambda: logging.getLogger(__name__))

    def __init__(self, **kwargs):
        """Initialize the search tool."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def search_web(self, query: str) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo."""
        try:
            results = list(self.ddgs.text(query, max_results=5))
            if not results:
                self.logger.warning(f"No results found for query: {query}")
                return []
            return results
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            return []

    async def _arun(self, query: str) -> List[Dict[str, Any]]:
        """Run the search asynchronously."""
        return self.search_web(query)

    def _run(self, query: str) -> List[Dict[str, Any]]:
        """Run the search tool synchronously."""
        raise NotImplementedError("Use _arun instead") 