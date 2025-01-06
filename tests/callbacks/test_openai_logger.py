"""Tests for OpenAI logger callback handler."""
import pytest
import logging
from datetime import datetime
from langchain_core.outputs import LLMResult, Generation
from langchain_core.messages import HumanMessage, SystemMessage
from src.callbacks.openai_logger import OpenAICallbackHandler
from src.config.logging_config import get_logger

@pytest.fixture
def callback_handler():
    """Create a callback handler instance for testing."""
    return OpenAICallbackHandler()

@pytest.mark.asyncio
async def test_on_llm_start(callback_handler, caplog):
    """Test request logging on LLM start."""
    caplog.set_level(logging.INFO)
    
    await callback_handler.on_llm_start(
        {"name": "gpt-4"},
        [HumanMessage(content="test prompt")],
        invocation_params={"request_id": "test-123", "temperature": 0.7}
    )
    
    assert "OpenAI Request - ID: test-123" in caplog.text
    assert "Temperature: 0.7" in caplog.text
    assert "Human: test prompt" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_start_with_string_messages(callback_handler, caplog):
    """Test request logging with string messages."""
    caplog.set_level(logging.INFO)
    
    await callback_handler.on_llm_start(
        {"name": "gpt-4"},
        ["test prompt", "another message"],
        invocation_params={"request_id": "test-123", "temperature": 0.7}
    )
    
    assert "OpenAI Request - ID: test-123" in caplog.text
    assert "Temperature: 0.7" in caplog.text
    assert "text: test prompt" in caplog.text
    assert "text: another message" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_start_empty_messages(callback_handler, caplog):
    """Test request logging with empty messages."""
    caplog.set_level(logging.INFO)
    
    await callback_handler.on_llm_start(
        {"name": "gpt-4"},
        [],
        invocation_params={"request_id": "test-123", "temperature": 0.7}
    )
    
    assert "OpenAI Request - ID: test-123" in caplog.text
    assert "Note: Empty messages list provided" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_end(callback_handler, caplog):
    """Test response logging on LLM end."""
    caplog.set_level(logging.INFO)
    
    # Create a mock LLMResult
    generation = Generation(
        text="test response",
        generation_info={"finish_reason": "stop"}
    )
    response = LLMResult(
        generations=[[generation]],
        llm_output={
            "model_name": "gpt-4",
            "token_usage": {
                "total_tokens": 100,
                "completion_tokens": 50,
                "prompt_tokens": 50
            }
        }
    )
    
    await callback_handler.on_llm_end(response, request_id="test-123")
    
    assert "OpenAI Response - ID: test-123" in caplog.text
    assert "test response" in caplog.text
    assert "Tokens Used:" in caplog.text
    assert "Total: 100" in caplog.text
    assert "Completion: 50" in caplog.text
    assert "Prompt: 50" in caplog.text
    assert "Finish Reason: stop" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_end_with_empty_response(callback_handler, caplog):
    """Test response logging with empty response."""
    caplog.set_level(logging.INFO)
    
    await callback_handler.on_llm_end(None)
    assert "Note: Empty response received (None)" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_end_with_no_generations(callback_handler, caplog):
    """Test response logging with no generations."""
    caplog.set_level(logging.INFO)
    
    response = LLMResult(generations=[], llm_output={})
    await callback_handler.on_llm_end(response)
    assert "Note: Response contains no generations" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_end_with_missing_data(callback_handler, caplog):
    """Test response logging with missing data."""
    caplog.set_level(logging.INFO)
    
    # Create a minimal LLMResult with no generation_info
    generation = Generation(text="test response")
    response = LLMResult(generations=[[generation]])
    
    await callback_handler.on_llm_end(response)
    
    assert "OpenAI Response - ID: N/A" in caplog.text
    assert "Content: test response" in caplog.text
    assert "Finish Reason: unknown" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_end_with_error(callback_handler, caplog):
    """Test response logging with formatting error."""
    caplog.set_level(logging.INFO)
    
    # Create a malformed response that will cause an error
    class BadResponse:
        @property
        def generations(self):
            raise AttributeError("Test error")
    
    await callback_handler.on_llm_end(BadResponse())
    assert "Note: Error formatting response: Test error" in caplog.text

@pytest.mark.asyncio
async def test_on_llm_error(callback_handler, caplog):
    """Test error logging on LLM error."""
    caplog.set_level(logging.ERROR)
    
    test_error = ValueError("Test error message")
    await callback_handler.on_llm_error(
        test_error,
        request_id="test-123"
    )
    
    assert "OpenAI Error - ID: test-123" in caplog.text
    assert "Error Type: ValueError" in caplog.text
    assert "Error Message: Test error message" in caplog.text

@pytest.mark.asyncio
async def test_missing_values_handled(callback_handler, caplog):
    """Test handling of missing values in responses."""
    caplog.set_level(logging.INFO)
    
    # Test with minimal data
    await callback_handler.on_llm_start(
        {"name": None},
        [SystemMessage(content="")],
        invocation_params={}
    )
    
    assert "Model: N/A" in caplog.text  # Should use default N/A for missing values 