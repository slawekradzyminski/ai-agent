import pytest
import pytest_asyncio
from src.memory.vector_memory import VectorMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

@pytest_asyncio.fixture
async def memory():
    memory = VectorMemory()
    yield memory
    memory.clear()

@pytest.mark.asyncio
async def test_add_and_retrieve_tool_memory(memory):
    memory.add_tool_memory("search", "python programming", "Python is a programming language")
    tool_outputs = memory.get_relevant_tool_outputs("python")
    assert len(tool_outputs) > 0
    assert tool_outputs[0]["tool"] == "search"
    assert "python programming" in tool_outputs[0]["input"].lower()

@pytest.mark.asyncio
async def test_add_and_retrieve_conversation_memory(memory):
    message1 = "Python is great for AI"
    message2 = "I agree, especially for machine learning"
    memory.add_user_message(message1)
    memory.add_ai_message(message2)
    
    # Test conversation context
    context = memory.get_conversation_context()
    assert len(context) == 2
    assert isinstance(context[0], HumanMessage)
    assert isinstance(context[1], AIMessage)
    assert context[0].content == message1
    assert context[1].content == message2

@pytest.mark.asyncio
async def test_get_relevant_tool_outputs(memory):
    memory.add_tool_memory("search", "python", "Python is a language")
    memory.add_tool_memory("browser", "java", "Java is a language")
    tool_outputs = memory.get_relevant_tool_outputs("python")
    assert len(tool_outputs) > 0
    assert tool_outputs[0]["tool"] == "search"
    assert "python" in tool_outputs[0]["input"].lower()

@pytest.mark.asyncio
async def test_clear_memory(memory):
    memory.add_tool_memory("search", "test", "result")
    memory.clear()
    tool_outputs = memory.get_relevant_tool_outputs("test")
    assert len(tool_outputs) == 0
    assert len(memory.get_conversation_context()) == 0

@pytest.mark.asyncio
async def test_parse_tool_output(memory):
    tool_output = "search: python programming -> Found information about Python"
    result = memory._parse_tool_output(tool_output)
    assert result["tool"] == "search"
    assert result["input"] == "python programming"
    assert result["output"] == "Found information about Python"

@pytest.mark.asyncio
async def test_memory_variables(memory):
    variables = memory.memory_variables
    assert "chat_history" in variables
    assert "tool_history" in variables

@pytest.mark.asyncio
async def test_empty_memory_search(memory):
    tool_outputs = memory.get_relevant_tool_outputs("test")
    assert len(tool_outputs) == 0
    
@pytest.mark.asyncio
async def test_filtered_search(memory):
    memory.add_tool_memory("search", "python", "Python info")
    memory.add_user_message("I love Python")
    
    # Search only tool outputs
    tool_outputs = memory.get_relevant_tool_outputs("python")
    assert len(tool_outputs) == 1
    assert tool_outputs[0]["tool"] == "search"

@pytest.mark.asyncio
async def test_load_memory_variables(memory):
    # Add some messages and tool outputs
    memory.add_user_message("What is Python?")
    memory.add_ai_message("Python is a programming language")
    memory.add_tool_memory("search", "python features", "Python is versatile and easy to learn")
    
    # Load memory variables
    memory_vars = memory.load_memory_variables({"input": "Python"})
    
    # Check chat history
    assert len(memory_vars["chat_history"]) == 2
    assert isinstance(memory_vars["chat_history"][0], HumanMessage)
    assert isinstance(memory_vars["chat_history"][1], AIMessage)
    
    # Check tool history
    assert len(memory_vars["tool_history"]) == 1
    assert isinstance(memory_vars["tool_history"][0], SystemMessage)
    assert "python features" in memory_vars["tool_history"][0].content 