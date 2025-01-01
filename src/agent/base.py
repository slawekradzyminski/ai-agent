"""Base agent implementation."""
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from src.config.settings import OPENAI_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE
from src.tools.search import SearchTool
from src.tools.httprequest import HTTPRequestTool
from src.tools.browser import BrowserTool
from src.memory.memory import Memory, ToolMemory

class Agent:
    """Base agent class with DuckDuckGo search and HTTP request capabilities."""

    def __init__(self):
        """Initialize the agent with necessary tools and models."""
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model=AGENT_MODEL,
            temperature=AGENT_TEMPERATURE
        )
        self.search_tool = SearchTool()
        self.http_tool = HTTPRequestTool()
        self.browser_tool = BrowserTool()
        self.memory = Memory()
        self._last_tool_memory: Optional[ToolMemory] = None

    def search(self, query: str) -> List[dict]:
        """
        Perform a web search using the DuckDuckGo tool.

        Args:
            query: Search query string

        Returns:
            List of search results
        """
        results = self.search_tool.search_web(query)
        
        # Store in memory
        self._last_tool_memory = self.memory.add_tool_memory(
            tool_name="search",
            input_data={"query": query},
            output_data=results
        )
        
        return results

    def http_request(self, url: str) -> Dict[str, Any]:
        """
        Make an HTTP request to a URL.

        Args:
            url: The URL to request

        Returns:
            Dictionary containing the response data
        """
        result = self.http_tool.request(url)
        
        # Store in memory
        self._last_tool_memory = self.memory.add_tool_memory(
            tool_name="http_request",
            input_data={"url": url},
            output_data=result
        )
        
        return result

    def get_page_content(self, url: str) -> str:
        """
        Get page content using Selenium Chrome browser.

        Args:
            url: The URL to open

        Returns:
            The page content as a string
        """
        content = self.browser_tool.get_page_content(url)
        
        # Store in memory
        self._last_tool_memory = self.memory.add_tool_memory(
            tool_name="browser",
            input_data={"url": url},
            output_data=content[:1000]  # Store truncated content to save memory
        )
        
        return content

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
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Get relevant tool outputs
        relevant_tools = self.memory.get_relevant_tool_outputs(message)
        
        # Store user message with any tool outputs since last message
        tool_outputs = [self._last_tool_memory] if self._last_tool_memory else []
        self.memory.add_conversation_memory(
            role="user",
            content=message,
            related_tool_outputs=tool_outputs
        )
        
        # Create context with conversation history and relevant tool outputs
        context = self.memory.get_conversation_context(max_entries=5)
        
        # Add context to the message
        context_message = (
            f"Previous conversation and relevant information:\n\n{context}\n\n"
            f"Current message: {message}"
        )
        
        # Add user message with context
        messages.append(HumanMessage(content=context_message))
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Store assistant response
        self.memory.add_conversation_memory(
            role="assistant",
            content=response.content,
            related_tool_outputs=[]
        )
        
        # Clear last tool memory
        self._last_tool_memory = None
        
        return response.content 