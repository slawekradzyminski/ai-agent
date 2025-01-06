"""Base agent module."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.browser import BrowserTool
from src.tools.search import SearchTool
from src.tools.http import HttpTool
from src.memory.vector_memory import VectorMemory
from src.callbacks.tool_output import ToolOutputCallbackHandler
from src.callbacks.openai_logger import OpenAICallbackHandler
from src.callbacks.tool_usage import ToolUsageCallback
from src.config.logging_config import get_logger
from src.config.prompts import SYSTEM_PROMPT

logger = get_logger('console')

class Agent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    openai_api_key: str = Field(..., description="OpenAI API key")
    memory: VectorMemory = Field(default_factory=VectorMemory)
    llm: Optional[ChatOpenAI] = None
    agent_executor: Optional[AgentExecutor] = None
    tools: List[Any] = Field(default_factory=list)
    callbacks: List[Any] = Field(default_factory=list)
    
    def __init__(self, openai_api_key: str, **kwargs):
        super().__init__(openai_api_key=openai_api_key, **kwargs)
        self.setup_agent()
        logger.info("Agent initialized successfully")
        
    def setup_agent(self):
        try:
            tool_callback = ToolOutputCallbackHandler(self.memory)
            openai_callback = OpenAICallbackHandler()
            usage_callback = ToolUsageCallback()
            self.callbacks = [tool_callback, openai_callback, usage_callback]
            
            self.llm = ChatOpenAI(
                temperature=0,
                model="gpt-4",
                openai_api_key=self.openai_api_key,
                callbacks=self.callbacks
            )
            
            self.tools = [
                SearchTool(name="search", callbacks=self.callbacks),
                BrowserTool(name="browser", callbacks=self.callbacks),
                HttpTool(name="http", callbacks=self.callbacks)
            ]
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                MessagesPlaceholder(variable_name="tool_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=False,
                handle_parsing_errors=True,
                callbacks=self.callbacks
            )
            
        except Exception as e:
            logger.error(f"Error setting up agent: {str(e)}")
            raise
            
    async def process_message(self, message: str) -> str:
        try:
            response = await self.agent_executor.ainvoke(
                {
                    "input": message
                }
            )
            
            output = response.get("output", "An error occurred while processing your request.")
            return output
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"An error occurred: {str(e)}"

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a web search using the SearchTool."""
        try:
            search_tool = next(tool for tool in self.tools if isinstance(tool, SearchTool))
            result = await search_tool._arun(query, run_manager=self.callbacks[0])
            return result
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return {"error": str(e)}

    async def get_page_content(self, url: str) -> Dict[str, Any]:
        """Get web page content using the BrowserTool."""
        try:
            browser_tool = next(tool for tool in self.tools if isinstance(tool, BrowserTool))
            result = await browser_tool._arun(url, run_manager=self.callbacks[0])
            return result
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return {"error": str(e)}

    async def make_http_request(self, url: str) -> Dict[str, Any]:
        """Make an HTTP request using the HttpTool."""
        try:
            http_tool = next(tool for tool in self.tools if isinstance(tool, HttpTool))
            result = await http_tool._arun(url, run_manager=self.callbacks[0])
            return result
        except Exception as e:
            logger.error(f"Error making HTTP request: {str(e)}")
            return {"error": str(e)} 