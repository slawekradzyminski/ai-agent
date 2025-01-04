"""Base agent module."""
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.agents.agent import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.browser import BrowserTool
from src.tools.search import SearchTool
from src.tools.http import HttpTool
from src.memory.memory import Memory

logger = logging.getLogger(__name__)

class Agent(BaseModel):
    """AI agent that can use tools to accomplish tasks."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    openai_api_key: str = Field(..., description="OpenAI API key")
    memory: Memory = Field(default_factory=Memory)
    llm: Optional[ChatOpenAI] = None
    agent_executor: Optional[AgentExecutor] = None
    tools: List[Any] = Field(default_factory=list)
    
    def __init__(self, openai_api_key: str, **kwargs):
        """Initialize the agent with tools and memory."""
        super().__init__(openai_api_key=openai_api_key, **kwargs)
        self.setup_agent()
        logger.info("Agent initialized successfully")

    def setup_agent(self):
        """Set up the agent with tools and LLM."""
        try:
            self.llm = ChatOpenAI(
                temperature=0,
                model="gpt-4",
                openai_api_key=self.openai_api_key
            )
            
            # Initialize tools with properly formatted names
            self.tools = [
                SearchTool(name="search"),
                BrowserTool(name="browser"),
                HttpTool(name="http")
            ]
            
            # Create the agent prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant that can use tools to accomplish tasks. When using tools, always try to extract the most relevant information and present it clearly to the user. You have access to the conversation history and the history of tool outputs to help provide context-aware responses."),
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
            
            # Create the agent executor with our custom memory
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True
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
        result = await search_tool._arun(query)
        self.memory.add_tool_memory("search", query, str(result))
        return result

    async def get_page_content(self, url: str) -> Dict[str, Any]:
        """Get web page content using the BrowserTool."""
        browser_tool = next(tool for tool in self.tools if isinstance(tool, BrowserTool))
        result = await browser_tool._arun(url)
        self.memory.add_tool_memory("browser", url, str(result))
        return result

    async def make_http_request(self, url: str) -> str:
        """Make an HTTP request using the HttpTool."""
        http_tool = next(tool for tool in self.tools if isinstance(tool, HttpTool))
        result = await http_tool._arun(url)
        self.memory.add_tool_memory("http", url, str(result))
        return result 