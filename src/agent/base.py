"""Base agent module."""
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.agents.agent import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.callbacks import BaseCallbackHandler
from src.tools.browser import BrowserTool
from src.tools.search import SearchTool
from src.tools.http import HttpTool
from src.memory.vector_memory import VectorMemory
from src.callbacks.tool_output import ToolOutputCallbackHandler
from src.callbacks.openai_logger import OpenAICallbackHandler
from src.config.logging_config import get_logger
from src.config.prompts import SYSTEM_PROMPT

# Use console logger for user interaction
logger = get_logger('console')

class ToolUsageCallback(BaseCallbackHandler):
    """Callback to show tool usage in console."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger('console')
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Show when a tool starts being used."""
        tool_name = serialized.get("name", "unknown")
        self.logger.info(f"\n> Using tool: {tool_name}")
        self.logger.info(f"> Input: {input_str}\n")
    
    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Show tool output."""
        self.logger.info(f"> Tool output received\n")

class Agent(BaseModel):
    """AI agent that can use tools to accomplish tasks."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    openai_api_key: str = Field(..., description="OpenAI API key")
    memory: VectorMemory = Field(default_factory=VectorMemory)
    llm: Optional[ChatOpenAI] = None
    agent_executor: Optional[AgentExecutor] = None
    tools: List[Any] = Field(default_factory=list)
    callbacks: List[Any] = Field(default_factory=list)
    
    def __init__(self, openai_api_key: str, **kwargs):
        """Initialize the agent with tools and memory."""
        super().__init__(openai_api_key=openai_api_key, **kwargs)
        self.setup_agent()
        logger.info("Agent initialized successfully")
        
    def setup_agent(self):
        """Set up the agent with tools and LLM."""
        try:
            # Create callback handlers
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
            
            # Initialize tools with properly formatted names and callbacks
            self.tools = [
                SearchTool(name="search", callbacks=self.callbacks),
                BrowserTool(name="browser", callbacks=self.callbacks),
                HttpTool(name="http", callbacks=self.callbacks)
            ]
            
            # Create the agent prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                MessagesPlaceholder(variable_name="tool_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Create the agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create the agent executor with our custom memory and callbacks
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=False,  # Set to False to reduce console output
                handle_parsing_errors=True,
                callbacks=self.callbacks
            )
            
        except Exception as e:
            logger.error(f"Error setting up agent: {str(e)}")
            raise
            
    async def process_message(self, message: str) -> str:
        """Process a user message and return the response."""
        try:
            # Process the message
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
        search_tool = next(tool for tool in self.tools if isinstance(tool, SearchTool))
        result = await search_tool._arun(query, run_manager=self.callbacks[0])
        return result

    async def get_page_content(self, url: str) -> Dict[str, Any]:
        """Get web page content using the BrowserTool."""
        browser_tool = next(tool for tool in self.tools if isinstance(tool, BrowserTool))
        result = await browser_tool._arun(url, run_manager=self.callbacks[0])
        return result

    async def make_http_request(self, url: str) -> str:
        """Make an HTTP request using the HttpTool."""
        try:
            logger.info(f"Finding HttpTool for URL: {url}")
            http_tool = next(tool for tool in self.tools if isinstance(tool, HttpTool))
            logger.info("Found HttpTool")
            
            if not self.callbacks:
                logger.warning("No callbacks available")
            else:
                logger.info("Using callback for tool execution")
                
            result = await http_tool._arun(url, run_manager=self.callbacks[0] if self.callbacks else None)
            logger.info("Successfully executed HTTP request")
            return result
        except Exception as e:
            logger.error(f"Error making HTTP request: {str(e)}")
            return {"error": str(e)} 