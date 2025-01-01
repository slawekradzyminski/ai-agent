"""Base agent implementation."""
import json
import uuid
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from src.config.settings import OPENAI_API_KEY, AGENT_MODEL, AGENT_TEMPERATURE
from src.tools.search import SearchTool
from src.tools.httprequest import HTTPRequestTool
from src.tools.browser import BrowserTool
from src.memory.memory import Memory, ToolMemory
from src.config.logging_config import request_logger

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
        self._recent_tool_memories: List[ToolMemory] = []

    async def search(self, query: str) -> List[dict]:
        """
        Perform a web search using the DuckDuckGo tool.

        Args:
            query: Search query string

        Returns:
            List of search results
        """
        results = self.search_tool.search_web(query)
        
        # Store in memory
        tool_memory = self.memory.add_tool_memory(
            tool_name="search",
            input_data={"query": query},
            output_data=results
        )
        self._recent_tool_memories.append(tool_memory)
        
        return results

    async def http_request(self, url: str) -> Dict[str, Any]:
        """
        Make an HTTP request to a URL.

        Args:
            url: The URL to request

        Returns:
            Dictionary containing the response data
        """
        result = self.http_tool.request(url)
        
        # Store in memory
        tool_memory = self.memory.add_tool_memory(
            tool_name="http_request",
            input_data={"url": url},
            output_data=result
        )
        self._recent_tool_memories.append(tool_memory)
        
        return result

    async def get_page_content(self, url: str) -> str:
        """
        Get content from a webpage using Chrome.

        Args:
            url: The URL to fetch content from

        Returns:
            String containing the page content
        """
        content = self.browser_tool.get_page_content(url)
        
        # Store in memory
        tool_memory = self.memory.add_tool_memory(
            tool_name="browser",
            input_data={"url": url},
            output_data={"url": url, "content": content}
        )
        self._recent_tool_memories.append(tool_memory)
        
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
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        messages = []
        
        # Use enhanced system prompt if none provided
        if system_prompt is None:
            system_prompt = (
                "You are a helpful AI assistant. When summarizing content:"
                "\n1. Identify and include all key points"
                "\n2. Preserve important details and examples"
                "\n3. Maintain context and relationships between ideas"
                "\n4. Include specific recommendations or resources mentioned"
                "\nBe thorough yet concise."
            )
        
        messages.append(SystemMessage(content=system_prompt))

        # Get relevant tool outputs
        relevant_tools = self.memory.get_relevant_tool_outputs(message)
        
        # Store user message with any tool outputs since last message
        self.memory.add_conversation_memory(
            role="user",
            content=message,
            related_tool_outputs=self._recent_tool_memories
        )
        
        # Create context with conversation history and relevant tool outputs
        context = self.memory.get_conversation_context(max_entries=5)
        
        # Format tool outputs for context
        tool_context = ""
        if self._recent_tool_memories:
            tool_context = "\nRecent tool outputs:\n"
            for tool in self._recent_tool_memories:
                if tool.tool_name == "browser" and "content" in tool.output_data:
                    tool_context += f"\nBrowser content from {tool.output_data['url']}:\n{tool.output_data['content']}\n"
                else:
                    tool_context += f"\n{tool.tool_name} output: {json.dumps(tool.output_data, indent=2)}\n"
        
        # Add context to the message
        context_message = (
            f"Previous conversation and relevant information:\n\n{context}\n"
            f"{tool_context}\n"
            f"Current message: {message}"
        )
        
        # Add user message with context
        messages.append(HumanMessage(content=context_message))

        # Log the OpenAI API request once with request ID
        request_data = {
            'request_id': request_id,
            'model': AGENT_MODEL,
            'messages': [
                {'role': 'system' if isinstance(msg, SystemMessage) else 'user',
                 'content': msg.content}
                for msg in messages
            ],
            'temperature': AGENT_TEMPERATURE
        }
        
        request_logger.info(
            "OpenAI API Request",
            extra={
                'request': json.dumps(request_data, indent=2),
                'response': 'Pending...'
            }
        )

        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Log the OpenAI API response once with request ID
        request_logger.info(
            "OpenAI API Response",
            extra={
                'request': f"Request ID: {request_id}",
                'response': response.content
            }
        )
        
        # Store assistant response
        self.memory.add_conversation_memory(
            role="assistant",
            content=response.content,
            related_tool_outputs=[]
        )
        
        # Clear recent tool memories
        self._recent_tool_memories = []
        
        return response.content 