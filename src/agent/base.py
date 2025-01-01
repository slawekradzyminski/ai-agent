"""Base agent implementation."""
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from src.config.settings import OPENAI_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE
from src.tools.search import SearchTool
from src.tools.httprequest import HTTPRequestTool

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
        self.conversation_history: List[dict] = []

    def search(self, query: str) -> List[dict]:
        """
        Perform a web search using the DuckDuckGo tool.

        Args:
            query: Search query string

        Returns:
            List of search results
        """
        return self.search_tool.search_web(query)

    def http_request(self, url: str) -> Dict[str, Any]:
        """
        Make an HTTP request to a URL.

        Args:
            url: The URL to request

        Returns:
            Dictionary containing the response data
        """
        return self.http_tool.request(url)

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

        # Add user message
        messages.append(HumanMessage(content=message))
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Store in conversation history
        self.conversation_history.append({
            "user": message,
            "assistant": response.content
        })
        
        return response.content 