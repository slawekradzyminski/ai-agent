"""Tests for the command-line interface."""
import asyncio
import pytest
from unittest.mock import Mock, patch

from src.cli import AgentCLI


@pytest.fixture
def cli():
    """Create a CLI instance with a mocked agent."""
    return AgentCLI()


@pytest.mark.asyncio
async def test_process_message(cli):
    """Test processing a single message."""
    with patch('langchain_openai.ChatOpenAI.invoke') as mock_chat:
        # Mock chat response
        mock_response = Mock()
        mock_response.content = "This is a test response."
        mock_chat.return_value = mock_response
        
        response = await cli.agent.process_message(
            "Hello, how are you?",
            system_prompt="You are a helpful AI assistant. Be concise."
        )
        assert isinstance(response, str)
        assert response == "This is a test response."


@pytest.mark.asyncio
async def test_search_command(cli):
    """Test the search command functionality."""
    with patch('src.tools.search.SearchTool.search_web') as mock_search:
        # Mock search results
        mock_search.return_value = [
            {
                'title': 'Test Result',
                'link': 'https://test.com',
                'snippet': 'Test snippet',
                'source': 'text'
            }
        ]
        
        results = cli.agent.search("test query")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]['title'] == 'Test Result'


@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
@pytest.mark.asyncio
async def test_interactive_mode_help(mock_print, mock_input, cli):
    """Test the interactive mode help command."""
    await cli.interactive_mode()
    # Verify help message was printed
    assert any('Available commands' in str(call) for call in mock_print.call_args_list)


@patch('builtins.input', side_effect=['search: test query', 'exit'])
@patch('builtins.print')
@pytest.mark.asyncio
async def test_interactive_mode_search(mock_print, mock_input, cli):
    """Test the interactive mode search command."""
    with patch('src.tools.search.SearchTool.search_web') as mock_search:
        # Mock search results
        mock_search.return_value = [
            {
                'title': 'Test Result',
                'link': 'https://test.com',
                'snippet': 'Test snippet',
                'source': 'text'
            }
        ]
        
        await cli.interactive_mode()
        # Verify search results were displayed
        assert any('Search Results for:' in str(call) for call in mock_print.call_args_list)
        assert any('Test Result' in str(call) for call in mock_print.call_args_list) 