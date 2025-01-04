"""Base agent implementation."""
import json
import uuid
from typing import List, Optional, Dict, Any, Tuple
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.tools import Tool, StructuredTool
from src.config.settings import OPENAI_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE
from src.tools.search import SearchTool
from src.tools.httprequest import HTTPRequestTool
from src.tools.browser import BrowserTool
from src.memory.memory import Memory, ToolMemory
from src.config.logging_config import request_logger
from datetime import datetime

class ChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores messages in memory."""
    
    def __init__(self):
        self.messages: List[BaseMessage] = []
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history."""
        self.messages.append(message)
    
    def clear(self) -> None:
        """Clear the message history."""
        self.messages = []

class Agent:
    """Base agent class with autonomous tool selection and execution."""

    def __init__(self):
        """Initialize the agent with necessary tools and models."""
        self.memory = Memory()
        self._recent_tool_memories: List[ToolMemory] = []
        self.chat_history = ChatMessageHistory()
        
        # Initialize tools
        self.search_tool = SearchTool()
        self.http_tool = HTTPRequestTool()
        self.browser_tool = BrowserTool()
        
        # Create Langchain tools
        self.tools = [
            Tool(
                name="web_search",
                description="Search the web using DuckDuckGo. Use this when you need to find general information about a topic.",
                func=self.search_tool.search_web,
                return_direct=False
            ),
            Tool(
                name="http_request",
                description="Make an HTTP request to a URL. Use this when you have a specific URL and want to get its content, especially for APIs or structured data.",
                func=self.http_tool.request,
                return_direct=False
            ),
            Tool(
                name="browser",
                description="Get content from a webpage using Chrome browser. Use this when you need to extract content from a webpage, especially for JavaScript-rendered content.",
                func=self.browser_tool.get_page_content,
                return_direct=False
            )
        ]
        
        # Initialize Langchain components
        self.llm = ChatOpenAI(
            model=AGENT_MODEL,
            temperature=AGENT_TEMPERATURE,
            api_key=OPENAI_API_KEY
        )
        
        # Create the agent with updated pattern
        system_message = SystemMessage(content="""You are a helpful AI assistant with access to various tools for retrieving information.
When using tools:
1. Choose the most appropriate tool for the task
2. Use web_search for general information gathering
3. Use browser for detailed webpage content extraction
4. Use http_request for API calls or when you have a specific URL
5. Cite sources when referencing information
6. Be clear about what information comes from tools vs. your knowledge
Be thorough yet concise.""")
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self._agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self._agent_executor = AgentExecutor(
            agent=self._agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        self.request_logger = request_logger
        
    @property
    def agent(self):
        """Get the agent instance."""
        return self._agent
        
    @property
    def agent_executor(self):
        """Get the agent executor instance."""
        return self._agent_executor

    async def process_message(
        self,
        message: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Process a user message and return a response.
        
        Args:
            message: User's input message
            system_prompt: Optional system prompt to guide the agent's behavior
            
        Returns:
            Agent's response as a string
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Add user message to chat history
            self.chat_history.add_message(HumanMessage(content=message))
            
            # Let the agent decide which tools to use and execute them
            result = await self.agent_executor.ainvoke(
                {
                    "input": message,
                    "chat_history": self.chat_history.messages
                },
                {"request_id": request_id}
            )
            
            response = result["output"]
            
            # Add assistant response to chat history
            self.chat_history.add_message(AIMessage(content=response))
            
            # Log the response
            request_logger.info(
                "Agent Response",
                extra={
                    'agent_response': {
                        'id': request_id,
                        'message': message,
                        'response': response,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
            
            # Store in memory
            self.memory.add_conversation_memory(
                role="assistant",
                content=response,
                related_tool_outputs=self._recent_tool_memories
            )
            
            # Clear recent tool memories
            self._recent_tool_memories = []
            
            return response
            
        except Exception as e:
            request_logger.error(
                "Agent Error",
                extra={
                    'agent_error': {
                        'id': request_id,
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
            raise 