"""Dynamic context building functionality."""
from typing import List, Tuple, Optional
import json
import tiktoken
from src.memory.memory import Memory, ToolMemory
from src.tools.search import SearchTool
from src.tools.browser import BrowserTool
from src.tools.httprequest import HTTPRequestTool
from src.config.logging_config import request_logger

class ContextBuilder:
    def __init__(self, memory: Memory, search_tool: SearchTool, browser_tool: BrowserTool, http_tool: HTTPRequestTool):
        self.memory = memory
        self.search_tool = search_tool
        self.browser_tool = browser_tool
        self.http_tool = http_tool
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        
    def truncate_context(self, context: str, max_tokens: int = 4000) -> str:
        """Truncate context to stay within token limits while preserving meaningful content.
        
        Args:
            context: The context string to truncate
            max_tokens: Maximum number of tokens allowed
            
        Returns:
            Truncated context string
        """
        tokens = self.tokenizer.encode(context)
        if len(tokens) <= max_tokens:
            return context
            
        # Reserve tokens for ellipsis
        ellipsis = " ... "
        ellipsis_tokens = len(self.tokenizer.encode(ellipsis))
        available_tokens = max_tokens - ellipsis_tokens
        
        # Split available tokens between start and end, favoring the start
        first_part = int(available_tokens * 0.7)  # 70% from start
        last_part = available_tokens - first_part  # 30% from end
        
        # Get the text for first and last parts
        first_text = self.tokenizer.decode(tokens[:first_part])
        last_text = self.tokenizer.decode(tokens[-last_part:])
        
        # Ensure first part ends with a complete word
        if not first_text.endswith(" "):
            first_text = first_text.rsplit(" ", 1)[0] + " "
            
        # Ensure last part starts with a complete word
        if not last_text.startswith(" "):
            last_text = " " + last_text.split(" ", 1)[1]
            
        return first_text + ellipsis + last_text
        
    def score_content_relevance(self, query: str, content: str) -> float:
        """Score content relevance to query using simple heuristics.
        
        Args:
            query: Search query
            content: Content to score
            
        Returns:
            Relevance score between 0 and 1
        """
        if not content:
            return 0.0
            
        # Convert to lowercase for comparison
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Split into words
        query_words = set(query_lower.split())
        
        # Calculate word match ratio
        matches = sum(1 for word in query_words if word in content_lower)
        word_match_ratio = matches / len(query_words) if query_words else 0
        
        # Consider content length (prefer medium length content)
        content_length = len(content)
        length_score = min(1.0, 1000 / max(content_length, 100))  # Penalize very short/long content
        
        # Combine scores (70% word matches, 30% length)
        return (0.7 * word_match_ratio) + (0.3 * length_score)

    async def build_context(self, query: str) -> Tuple[str, List[ToolMemory]]:
        """Build context dynamically using available tools.
        
        Args:
            query: User's query to build context for
            
        Returns:
            Tuple of (context string, list of tool memories)
        """
        tool_memories = []
        context_parts = []
        
        try:
            search_results = self.search_tool.search_web(query)
            if search_results:
                tool_memory = self.memory.add_tool_memory(
                    tool_name="search",
                    input_data={"query": query},
                    output_data=search_results
                )
                tool_memories.append(tool_memory)
                context_parts.append("Search Results:")
                
                # Score and sort results by relevance
                scored_contents = []
                
                for result in search_results[:3]:  # Process top 3 results
                    url = result.get("link")
                    if not url:
                        continue
                        
                    try:
                        content = self.browser_tool.get_page_content(url)
                        if content:
                            relevance = self.score_content_relevance(query, content)
                            scored_contents.append((content, url, relevance, "browser"))
                            continue
                    except Exception as e:
                        request_logger.warning(f"Browser fetch failed for {url}: {str(e)}")
                    
                    try:
                        http_result = self.http_tool.request(url)
                        if "error" not in http_result:
                            if isinstance(http_result.get('data'), dict):
                                content = http_result['data'].get('content', json.dumps(http_result['data'], indent=2))
                            else:
                                content = str(http_result.get('data', ''))
                                
                            relevance = self.score_content_relevance(query, content)
                            scored_contents.append((content, url, relevance, "http_request"))
                    except Exception as e:
                        request_logger.warning(f"HTTP request failed for {url}: {str(e)}")
                
                # Sort by relevance and add to context
                scored_contents.sort(key=lambda x: x[2], reverse=True)
                for content, url, relevance, tool_type in scored_contents:
                    tool_memory = self.memory.add_tool_memory(
                        tool_name=tool_type,
                        input_data={"url": url},
                        output_data={"url": url, "content": content, "relevance": relevance}
                    )
                    tool_memories.append(tool_memory)
                    context_parts.append(f"\nContent from {url} (relevance: {relevance:.2f}):")
                    context_parts.append(content[:1000])  # Limit individual content length
                    
        except Exception as e:
            request_logger.error(f"Error building context: {str(e)}")
            return "", []  # Return empty context on error
        
        context = "\n".join(context_parts)
        context = self.truncate_context(context)  # Ensure we stay within token limits
        
        request_logger.info(
            "Dynamic context built",
            extra={
                'context_building': {
                    'query': query,
                    'num_sources': len(tool_memories),
                    'context_length': len(context),
                    'token_count': len(self.tokenizer.encode(context))
                }
            }
        )
        
        return context, tool_memories

    def format_tool_context(self, tool_memories: List[ToolMemory]) -> str:
        """Format tool memories into a context string."""
        if not tool_memories:
            return ""
            
        context_parts = ["\nRecent tool outputs:"]
        for tool in tool_memories:
            if tool.tool_name == "browser" and "content" in tool.output_data:
                context_parts.append(f"\nBrowser content from {tool.output_data['url']}:\n{tool.output_data['content']}")
            else:
                context_parts.append(f"\n{tool.tool_name} output: {json.dumps(tool.output_data, indent=2)}")
                
        return "\n".join(context_parts) 