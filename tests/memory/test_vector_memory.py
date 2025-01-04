import pytest
import pytest_asyncio
from src.memory.vector_memory import VectorMemory

@pytest_asyncio.fixture
async def memory():
    memory = VectorMemory()
    yield memory
    memory.clear()

@pytest.mark.asyncio
async def test_add_and_retrieve_tool_memory(memory):
    await memory.add_tool_memory("search", "python programming", "Python is a programming language")
    results = await memory.get_relevant_context("python")
    assert len(results) > 0
    assert "python programming" in results[0].lower()

@pytest.mark.asyncio
async def test_add_and_retrieve_conversation_memory(memory):
    message1 = "Python is great for AI"
    message2 = "I agree, especially for machine learning"
    await memory.add_conversation_memory(message1, True)
    await memory.add_conversation_memory(message2, False)
    results = await memory.get_relevant_context("artificial intelligence")
    assert len(results) > 0
    # Both messages should be relevant to AI/ML
    assert any("Python" in result for result in results)
    assert any("machine learning" in result for result in results)

@pytest.mark.asyncio
async def test_get_relevant_tool_outputs(memory):
    await memory.add_tool_memory("search", "python", "Python is a language")
    await memory.add_tool_memory("browser", "java", "Java is a language")
    results = await memory.get_relevant_tool_outputs("python")
    assert len(results) > 0
    assert results[0]["tool"] == "search"
    assert "python" in results[0]["input"].lower()

@pytest.mark.asyncio
async def test_clear_memory(memory):
    await memory.add_tool_memory("search", "test", "result")
    memory.clear()
    results = await memory.get_relevant_context("test")
    assert len(results) == 0

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
    assert "history" in variables
    assert "tool_outputs" in variables

@pytest.mark.asyncio
async def test_empty_memory_search(memory):
    results = await memory.get_relevant_context("test")
    assert len(results) == 0
    
@pytest.mark.asyncio
async def test_filtered_search(memory):
    await memory.add_tool_memory("search", "python", "Python info")
    await memory.add_conversation_memory("I love Python", True)
    
    # Search only tool outputs
    results = await memory.get_relevant_tool_outputs("python")
    assert len(results) == 1
    assert results[0]["tool"] == "search"

@pytest.mark.asyncio
async def test_save_and_load_context(memory):
    inputs = {"input": "What is Python?"}
    outputs = {"output": "Python is a programming language"}
    memory.save_context(inputs, outputs)
    
    memory_vars = memory.load_memory_variables({"input": "Python"})
    assert len(memory_vars["history"]) == 2
    assert memory_vars["history"][0].content == "What is Python?"
    assert memory_vars["history"][1].content == "Python is a programming language" 