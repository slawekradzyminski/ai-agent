import pytest
from unittest.mock import Mock, AsyncMock
from src.cli.handlers.memory import MemoryHandler

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.memory = Mock()
    agent.memory._documents = ["doc1", "doc2"]
    agent.memory._metadatas = [{"type": "test1"}, {"type": "test2"}]
    agent.memory._tool_outputs = [{"tool": "test", "input": "in", "output": "out"}]
    agent.memory._messages = [Mock(content="message1"), Mock(content="message2")]
    agent.memory.get_relevant_tool_outputs = AsyncMock(return_value=[{"tool": "test", "input": "query", "output": "result"}])
    return agent

@pytest.fixture
def handler(mock_agent):
    return MemoryHandler(mock_agent)

def test_can_handle(handler):
    assert handler.can_handle("memory documents")
    assert handler.can_handle("memory metadata")
    assert handler.can_handle("memory tools")
    assert handler.can_handle("memory messages")
    assert handler.can_handle("memory search test")
    assert not handler.can_handle("search test")
    assert not handler.can_handle("help")

@pytest.mark.asyncio
async def test_handle_documents(handler):
    result = await handler.handle("memory documents")
    assert "doc1" in result
    assert "doc2" in result

@pytest.mark.asyncio
async def test_handle_metadata(handler):
    result = await handler.handle("memory metadata")
    assert "test1" in result
    assert "test2" in result

@pytest.mark.asyncio
async def test_handle_tools(handler):
    result = await handler.handle("memory tools")
    assert "test" in result
    assert "in" in result
    assert "out" in result

@pytest.mark.asyncio
async def test_handle_messages(handler):
    result = await handler.handle("memory messages")
    assert "message1" in result
    assert "message2" in result

@pytest.mark.asyncio
async def test_handle_search(handler, mock_agent):
    result = await handler.handle("memory search test query")
    mock_agent.memory.get_relevant_tool_outputs.assert_called_once_with("test query")
    assert "test" in result
    assert "query" in result
    assert "result" in result

@pytest.mark.asyncio
async def test_handle_invalid(handler):
    result = await handler.handle("memory invalid")
    assert "Memory inspection commands" in result
    assert "memory documents" in result
    assert "memory metadata" in result
    assert "memory tools" in result
    assert "memory messages" in result
    assert "memory search" in result

def test_get_help(handler):
    help_text = handler.get_help()
    assert "Memory inspection commands" in help_text
    assert "memory documents" in help_text
    assert "memory metadata" in help_text
    assert "memory tools" in help_text
    assert "memory messages" in help_text
    assert "memory search" in help_text 