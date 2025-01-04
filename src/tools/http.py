"""HTTP tool for making web requests."""
import logging
import aiohttp
from typing import Dict, Any, Optional, Literal
from pydantic import Field
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)

class HttpTool(BaseTool):
    """Tool for making HTTP requests."""
    
    name: Literal["http"] = Field(default="http")
    description: Literal["Make an HTTP request to a URL"] = Field(default="Make an HTTP request to a URL")
    logger: logging.Logger = Field(default_factory=lambda: logging.getLogger(__name__))

    def __init__(self, **kwargs):
        """Initialize the HTTP tool."""
        super().__init__(**kwargs)
        self.logger = logger
        logger.info("Initializing HttpTool")

    async def _arun(self, url: str) -> str:
        """Run the HTTP tool asynchronously."""
        self.logger.info(f"HTTP Request initiated to: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    content_type = response.headers.get('Content-Type', '').split(';')[0]
                    content = await response.text()
                    
                    self.logger.info(
                        f"HTTP Request completed: status={response.status}, "
                        f"type={content_type}, length={len(content)} chars"
                    )
                    
                    return content if content_type != 'application/json' else await response.json()
                    
        except Exception as e:
            self.logger.error(f"HTTP Request failed: {str(e)}")
            raise

    def _run(self, url: str) -> str:
        """Run the HTTP tool synchronously."""
        raise NotImplementedError("Use _arun instead") 