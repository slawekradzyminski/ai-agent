import pytest
from unittest.mock import AsyncMock, Mock, patch
from langchain_core.outputs import LLMResult, Generation
from src.agent.base import Agent
from src.callbacks.tool_output import ToolOutputCallbackHandler
from src.callbacks.openai_logger import OpenAICallbackHandler

@pytest.fixture
def agent():
    with patch('src.agent.base.ChatOpenAI'), \
         patch('src.agent.base.create_openai_functions_agent'), \
         patch('src.agent.base.AgentExecutor') as mock_executor_class:
        mock_executor = Mock()
        mock_executor.ainvoke = AsyncMock(return_value={"output": "test response"})
        mock_executor_class.return_value = mock_executor
        
        agent = Agent(openai_api_key="test-key")
        
        mock_executor.callbacks = [
            ToolOutputCallbackHandler(agent.memory),
            OpenAICallbackHandler()
        ]
        
        return agent

@pytest.mark.asyncio
async def test_process_message_with_tool_selection(agent):
    response = await agent.process_message("Search for test query")
    assert response == "test response"
    agent.agent_executor.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_with_multiple_tools(agent):
    response = await agent.process_message("Search and browse test.com")
    assert response == "test response"
    agent.agent_executor.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_error_handling(agent):
    agent.agent_executor.ainvoke.side_effect = Exception("Test error")
    response = await agent.process_message("Test message")
    assert "error" in response.lower()
    agent.agent_executor.ainvoke.assert_called_once()

def test_tool_descriptions(agent):
    for tool in agent.tools:
        assert tool.name is not None
        assert tool.description is not None

@pytest.mark.asyncio
async def test_autonomous_tool_output_storage(agent):
    tool_name = "search"
    tool_input = "weather in London"
    tool_output = "Cloudy with a chance of rain"
    
    async def mock_ainvoke(inputs):
        tool_callback = agent.agent_executor.callbacks[0]
        await tool_callback.on_tool_end(
            tool_output,
            tool_name=tool_name,
            tool_input=tool_input
        )
        return {"output": "It's cloudy in London"}
    
    agent.agent_executor.ainvoke = AsyncMock(side_effect=mock_ainvoke)
    
    await agent.process_message("What's the weather in London?")
    
    tool_outputs = agent.memory.get_relevant_tool_outputs("weather London")
    assert len(tool_outputs) > 0
    assert any(
        output["tool"] == tool_name and
        output["input"] == tool_input and
        output["output"] == tool_output
        for output in tool_outputs
    )

@pytest.mark.asyncio
async def test_openai_logging(agent, caplog):
    caplog.set_level("INFO")
    
    async def mock_ainvoke(inputs):
        openai_callback = agent.agent_executor.callbacks[1]
        await openai_callback.on_llm_start(
            {"name": "gpt-4"},
            ["test prompt"],
            invocation_params={"request_id": "test-123", "temperature": 0.7}
        )
        await openai_callback.on_llm_end(
            LLMResult(
                generations=[[Generation(
                    text="test response",
                    generation_info={"finish_reason": "stop"}
                )]],
                llm_output={
                    "model_name": "gpt-4",
                    "token_usage": {
                        "total_tokens": 100,
                        "completion_tokens": 50,
                        "prompt_tokens": 50
                    }
                }
            ),
            request_id="test-123"
        )
        return {"output": "test response"}
    
    agent.agent_executor.ainvoke = AsyncMock(side_effect=mock_ainvoke)
    
    await agent.process_message("Test message")
    
    assert "OpenAI Request - ID: test-123" in caplog.text
    assert "Model: gpt-4" in caplog.text
    assert "Temperature: 0.7" in caplog.text
    assert "test prompt" in caplog.text
    assert "OpenAI Response - ID: test-123" in caplog.text
    assert "test response" in caplog.text
    assert "Tokens Used:" in caplog.text
    assert "Total: 100" in caplog.text
    assert "Completion: 50" in caplog.text
    assert "Prompt: 50" in caplog.text
    assert "Finish Reason: stop" in caplog.text 