"""HTTP tool for making web requests."""
import logging
import aiohttp
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun, BaseCallbackHandler

logger = logging.getLogger(__name__)

class HttpTool(BaseTool):
    """Tool for making HTTP requests."""
    
    name: str = Field(default="http", description="The name of the tool")
    description: str = Field(default="Make an HTTP request to a URL", description="The description of the tool")
    logger: logging.Logger = Field(default_factory=lambda: logging.getLogger(__name__))
    callbacks: Optional[List[BaseCallbackHandler]] = Field(default=None, description="Callbacks for the tool")

    def __init__(self, **kwargs):
        """Initialize the HTTP tool."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing HttpTool")

    async def make_request(self, url: str) -> Union[Dict[str, Any], str]:
        """Make an HTTP request to the given URL."""
        if not url:
            self.logger.error("URL is empty")
            return {"error": "URL cannot be empty"}

        self.logger.info(f"Making HTTP request to {url}")
        try:
            async with aiohttp.ClientSession() as session:
                self.logger.info("Created aiohttp session")
                async with session.get(url) as response:
                    self.logger.info(f"Got response with status {response.status}")
                    content_type = response.headers.get('Content-Type', '')
                    self.logger.info(f"Content-Type: {content_type}")
                    
                    if 'application/json' in content_type:
                        result = await response.json()
                        self.logger.info("Successfully parsed JSON response")
                        return result
                    else:
                        result = await response.text()
                        self.logger.info("Successfully got text response")
                        return result
                        
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP request error: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in make_request: {str(e)}")
            return {"error": str(e)}

    async def _arun(
        self,
        url: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """Run the HTTP tool asynchronously."""
        try:
            self.logger.info(f"Starting _arun with URL: {url}")
            result = await self.make_request(url)
            self.logger.info("Got result from make_request")
            
            if run_manager:
                self.logger.info("Calling run_manager.on_tool_end")
                try:
                    # Convert result to a string representation for the callback
                    output = str(result) if isinstance(result, str) else str(result.get("error", result))
                    await run_manager.on_tool_end(
                        output=output,
                        tool_input=url,
                        tool_name=self.name
                    )
                    self.logger.info("Successfully called run_manager.on_tool_end")
                except Exception as e:
                    self.logger.error(f"Error in callback: {str(e)}")
                    # Continue even if callback fails
            else:
                self.logger.warning("run_manager is None")
                
            return result
        except Exception as e:
            self.logger.error(f"Error in _arun: {str(e)}")
            raise

    def _run(self, url: str) -> Union[Dict[str, Any], str]:
        """Run the HTTP tool synchronously."""
        raise NotImplementedError("Use _arun instead") 