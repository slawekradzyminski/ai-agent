import logging
from typing import Optional, List, Dict, Any
from pydantic import Field
from duckduckgo_search import DDGS
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun, BaseCallbackHandler

logger = logging.getLogger(__name__)

class SearchTool(BaseTool):
    name: str = Field(default="search", description="The name of the tool")
    description: str = Field(default="Search the web for information about a topic", description="The description of the tool")
    ddgs: Optional[DDGS] = Field(default_factory=DDGS)
    logger: logging.Logger = Field(default_factory=lambda: logging.getLogger(__name__))
    callbacks: Optional[List[BaseCallbackHandler]] = Field(default=None, description="Callbacks for the tool")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def search_web(self, query: str) -> List[Dict[str, Any]]:
        try:
            results = list(self.ddgs.text(query, max_results=5))
            if not results:
                self.logger.warning(f"No results found for query: {query}")
                return []
            return results
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            return []

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Run the search asynchronously."""
        try:
            results = self.search_web(query)
            if run_manager:
                try:
                    output = "\n".join(f"{r['title']}: {r['body']}" for r in results)
                    await run_manager.on_tool_end(
                        output=output,
                        tool_input=query,
                        tool_name=self.name
                    )
                except Exception as e:
                    self.logger.error(f"Error in callback: {str(e)}")
                    # Continue even if callback fails
            return results
        except Exception as e:
            self.logger.error(f"Error in _arun: {str(e)}")
            raise

    def _run(self, query: str) -> List[Dict[str, Any]]:
        """Run the search tool synchronously."""
        raise NotImplementedError("Use _arun instead") 