"""Tests for the context builder module."""
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from src.memory.memory import Memory
from src.context.builder import build_context, truncate_context, score_content_relevance, format_tool_context

@pytest.fixture
def memory():
    """Create a memory instance for testing."""
    return Memory()

@pytest.mark.asyncio
async def test_build_context_success(memory):
    """Test building context with successful tool executions."""
    # Add some tool outputs to memory
    memory.add_tool_memory("search", "test query", "test search result")
    memory.add_tool_memory("browser", "test.com", "test webpage content")
    memory.add_tool_memory("http", "test.com/api", "test api response")
    
    # Add some conversation context
    memory.add_user_message("What is the test about?")
    memory.add_ai_message("Let me search for that information.")
    
    context = await build_context("test query", memory)
    assert "Tool: search" in context
    assert "Input: test query" in context
    assert "Output: test search result" in context
    assert "Tool: browser" in context
    assert "Input: test.com" in context
    assert "Output: test webpage content" in context
    assert "Tool: http" in context
    assert "Input: test.com/api" in context
    assert "Output: test api response" in context
    assert "User: What is the test about?" in context
    assert "Assistant: Let me search for that information." in context

@pytest.mark.asyncio
async def test_build_context_search_failure(memory):
    """Test building context when search tool fails."""
    # Mock failed search
    memory.add_tool_memory("search", "test query", "error: Search failed")
    
    context = await build_context("test query", memory)
    assert "Tool: search" in context
    assert "Input: test query" in context
    assert "Output: error: Search failed" in context

@pytest.mark.asyncio
async def test_build_context_browser_failure(memory):
    """Test building context when browser tool fails."""
    # Mock failed browser request
    memory.add_tool_memory("browser", "test.com", "error: Browser failed")
    
    context = await build_context("test query", memory)
    assert "Tool: browser" in context
    assert "Input: test.com" in context
    assert "Output: error: Browser failed" in context

@pytest.mark.asyncio
async def test_build_context_http_failure(memory):
    """Test building context when HTTP tool fails."""
    # Mock failed HTTP request
    memory.add_tool_memory("http", "test.com/api", "error: HTTP request failed")
    
    context = await build_context("test query", memory)
    assert "Tool: http" in context
    assert "Input: test.com/api" in context
    assert "Output: error: HTTP request failed" in context

def test_truncate_context():
    """Test context truncation."""
    long_context = "a" * 5000
    truncated = truncate_context(long_context, max_length=1000)
    assert len(truncated) <= 1000
    assert truncated.endswith("...")

def test_score_content_relevance():
    """Test content relevance scoring."""
    query = "python programming"
    content = "Python is a popular programming language"
    score = score_content_relevance(query, content)
    assert 0 <= score <= 1.0  # Score should be between 0 and 1

def test_format_tool_context():
    """Test formatting tool outputs into context."""
    tool_outputs = [
        {
            "tool": "search",
            "input": "test query",
            "output": "test result"
        },
        {
            "tool": "browser",
            "input": "test.com",
            "output": "test content"
        }
    ]
    
    context = format_tool_context(tool_outputs)
    assert "Tool: search" in context
    assert "Input: test query" in context
    assert "Output: test result" in context
    assert "Tool: browser" in context 