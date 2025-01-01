"""Tests for agent memory integration."""
import pytest
from unittest.mock import Mock, patch
from src.agent.base import Agent
from src.memory.memory import Memory, ToolMemory

@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    with patch('src.agent.base.ChatOpenAI'):  # Mock the LLM to avoid API calls
        return Agent()

@pytest.mark.asyncio
async def test_browser_content_memory_storage(agent):
    """Test that browser content is properly stored in memory."""
    # Mock browser content
    test_url = "https://test.com"
    test_content = "Test page content"
    agent.browser_tool.get_page_content = Mock(return_value=test_content)
    
    # Get page content
    content = await agent.get_page_content(test_url)
    
    # Verify content is returned correctly
    assert content == test_content
    
    # Verify content is stored in memory correctly
    assert len(agent._recent_tool_memories) == 1
    tool_memory = agent._recent_tool_memories[0]
    assert tool_memory.tool_name == "browser"
    assert tool_memory.input_data == {"url": test_url}
    assert tool_memory.output_data == {"url": test_url, "content": test_content}

@pytest.mark.asyncio
async def test_browser_content_in_message_context(agent):
    """Test that browser content is included in message context."""
    # Mock browser content
    test_url = "https://test.com"
    test_content = "Test page content"
    agent.browser_tool.get_page_content = Mock(return_value=test_content)
    
    # First get page content
    await agent.get_page_content(test_url)
    
    # Mock LLM to capture the context
    context_captured = None
    def mock_invoke(messages):
        nonlocal context_captured
        context_captured = messages[0].content if messages else None
        return Mock(content="Test response")
    
    agent.llm.invoke = Mock(side_effect=mock_invoke)
    
    # Process a message
    response = await agent.process_message("What's in the page?")
    
    # Verify browser content is in context
    assert context_captured is not None
    assert test_url in context_captured
    assert test_content in context_captured
    
    # Verify tool memories are cleared after processing
    assert len(agent._recent_tool_memories) == 0

@pytest.mark.asyncio
async def test_multiple_tool_outputs_in_context(agent):
    """Test that multiple tool outputs are properly included in context."""
    # Mock browser and search content
    test_url = "https://test.com"
    test_content = "Test page content"
    agent.browser_tool.get_page_content = Mock(return_value=test_content)
    
    search_results = [{"title": "Test", "link": "https://test.com"}]
    agent.search_tool.search_web = Mock(return_value=search_results)
    
    # Execute tools
    await agent.get_page_content(test_url)
    await agent.search("test query")
    
    # Verify both tools are stored
    assert len(agent._recent_tool_memories) == 2
    
    # Mock LLM to capture the context
    context_captured = None
    def mock_invoke(messages):
        nonlocal context_captured
        context_captured = messages[0].content if messages else None
        return Mock(content="Test response")
    
    agent.llm.invoke = Mock(side_effect=mock_invoke)
    
    # Process a message
    response = await agent.process_message("What did you find?")
    
    # Verify both tool outputs are in context
    assert context_captured is not None
    assert test_url in context_captured
    assert test_content in context_captured
    assert str(search_results) in context_captured
    
    # Verify tool memories are cleared after processing
    assert len(agent._recent_tool_memories) == 0 