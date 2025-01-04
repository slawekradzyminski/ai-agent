"""Context builder module for generating context from tool outputs."""
import logging
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from src.memory.memory import Memory

logger = logging.getLogger(__name__)

async def build_context(query: str, memory: Memory) -> str:
    """Build context from tool outputs and conversation history."""
    try:
        # Get relevant tool outputs
        tool_outputs = memory.get_relevant_tool_outputs(query)
        
        # Format tool outputs into context
        tool_context = format_tool_context(tool_outputs)
        
        # Get conversation context
        conversation_context = memory.get_conversation_context()
        conversation_str = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in conversation_context
        ])
        
        # Combine contexts
        full_context = f"{tool_context}\n\nConversation History:\n{conversation_str}"
        
        # Truncate if too long
        return truncate_context(full_context)
        
    except Exception as e:
        logger.error(f"Error building context: {str(e)}")
        return ""

def truncate_context(context: str, max_length: int = 4000) -> str:
    """Truncate context to max_length characters."""
    if len(context) <= max_length:
        return context
    return context[:max_length - 3] + "..."

def score_content_relevance(query: str, content: str) -> float:
    """Score the relevance of content to a query."""
    # Simple word overlap scoring
    query_words = set(query.lower().split())
    content_words = set(content.lower().split())
    
    if not query_words or not content_words:
        return 0.0
    
    overlap = len(query_words.intersection(content_words))
    return overlap / len(query_words)

def format_tool_context(tool_outputs: List[Dict[str, Any]]) -> str:
    """Format tool outputs into a readable context string."""
    if not tool_outputs:
        return "No relevant tool outputs found."
    
    context_parts = []
    for output in tool_outputs:
        context_parts.append(f"[Tool: {output['tool']}]")
        context_parts.append(f"Input: {output['input']}")
        context_parts.append(f"Output: {output['output']}\n")
    
    return "\n".join(context_parts) 