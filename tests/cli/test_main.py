import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.cli.main import CLI

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.process_message = AsyncMock(return_value="test response")
    return agent

@pytest.fixture
def cli(mock_agent):
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        cli = CLI()
        cli.agent = mock_agent
        return cli

@pytest.mark.asyncio
async def test_process_command_help(cli):
    result = await cli.process_command("help")
    assert "Available commands" in result
    assert "help" in result
    assert "exit" in result

@pytest.mark.asyncio
async def test_process_command_chat(cli, mock_agent):
    result = await cli.process_command("hello")
    mock_agent.process_message.assert_called_once_with("hello")
    assert result == "test response"