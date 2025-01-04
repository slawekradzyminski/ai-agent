"""Test context builder module."""
import pytest
from unittest.mock import Mock, AsyncMock
from src.context.builder import build_context, truncate_context, score_content_relevance, format_tool_context
from src.memory.memory import Memory, ToolMemory

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
    assert "test search result" in context
    assert "test webpage content" in context
    assert "test api response" in context

@pytest.mark.asyncio
async def test_build_context_search_failure(memory):
    """Test building context when search tool fails."""
    # Mock failed search
    memory.add_tool_memory("search", "test query", "Error: Search failed")
    
    context = await build_context("test query", memory)
    assert "Error: Search failed" in context

@pytest.mark.asyncio
async def test_build_context_browser_failure(memory):
    """Test building context when browser tool fails."""
    # Mock failed browser request
    memory.add_tool_memory("browser", "test.com", "Error: Browser failed")
    
    context = await build_context("test query", memory)
    assert "Error: Browser failed" in context

@pytest.mark.asyncio
async def test_build_context_http_failure(memory):
    """Test building context when HTTP tool fails."""
    # Mock failed HTTP request
    memory.add_tool_memory("http", "test.com/api", "Error: HTTP request failed")
    
    context = await build_context("test query", memory)
    assert "Error: HTTP request failed" in context

def test_truncate_context(memory):
    """Test context truncation."""
    long_context = "a" * 10000  # Create a long string
    truncated = truncate_context(long_context, max_length=1000)
    assert len(truncated) <= 1000
    assert truncated.endswith("...")

def test_score_content_relevance(memory):
    """Test content relevance scoring."""
    query = "python programming"
    content = "Python is a popular programming language"
    score = score_content_relevance(query, content)
    assert 0 <= score <= 1.0  # Score should be between 0 and 1

def test_format_tool_context(memory):
    """Test formatting tool outputs into context."""
    tool_outputs = [
        {"tool": "search", "input": "test query", "output": "test result"},
        {"tool": "browser", "input": "test.com", "output": "test content"}
    ]
    
    context = format_tool_context(tool_outputs)
    assert "[Tool: search]" in context
    assert "Input: test query" in context
    assert "Output: test result" in context
    assert "[Tool: browser]" in context 