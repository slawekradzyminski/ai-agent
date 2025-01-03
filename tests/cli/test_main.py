"""Tests for the main CLI functionality."""
import pytest
from unittest.mock import Mock, patch, call, AsyncMock, MagicMock
import io
import sys

from src.cli.main import AgentCLI

@pytest.fixture
def cli():
    """Create a CLI instance for testing."""
    with patch('src.cli.main.Agent') as mock_agent_class:
        mock_agent = AsyncMock()
        mock_agent_class.return_value = mock_agent
        cli = AgentCLI()
        cli.agent = mock_agent
        return cli

class TestAgentCLI:
    """Tests for the AgentCLI class."""

    @pytest.mark.asyncio
    async def test_process_single_message_search(self, cli):
        """Test processing a search command."""
        mock_results = [{"title": "Test", "link": "http://test.com"}]
        async def mock_search(*args, **kwargs):
            return mock_results
        cli.agent.search = mock_search
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("search: python")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert "Test" in printed_text
            assert "http://test.com" in printed_text

    @pytest.mark.asyncio
    async def test_process_single_message_http(self, cli):
        """Test processing an HTTP command."""
        mock_response = {
            'status_code': 200,
            'content_type': 'application/json',
            'data': {'status': 'ok'}
        }
        async def mock_http_request(*args, **kwargs):
            return mock_response
        cli.agent.http_request = mock_http_request
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("http: example.com")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert "status" in printed_text
            assert "ok" in printed_text

    @pytest.mark.asyncio
    async def test_process_single_message_browser(self, cli):
        """Test processing a browser command."""
        mock_content = "Page content"
        async def mock_get_page_content(*args, **kwargs):
            return mock_content
        cli.agent.get_page_content = mock_get_page_content
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("browser: example.com")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert mock_content in printed_text

    @pytest.mark.asyncio
    async def test_process_single_message_chat(self, cli):
        """Test processing a chat message."""
        mock_response = "Assistant response"
        async def mock_process_message(*args, **kwargs):
            return mock_response
        cli.agent.process_message = mock_process_message
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("Hello")
            mock_print.assert_called_with("\nAssistant: Assistant response")

    @pytest.mark.asyncio
    async def test_process_single_message_http_error_handling(self, cli):
        """Test HTTP error handling in message processing."""
        mock_error = {"error": "Connection failed"}
        async def mock_http_request(*args, **kwargs):
            return mock_error
        cli.agent.http_request = mock_http_request
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("http: example.com")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert "Error" in printed_text
            assert "Connection failed" in printed_text

    @pytest.mark.asyncio
    async def test_process_single_message_browser_long_content(self, cli):
        """Test browser content truncation in message processing."""
        mock_content = "A" * 1000  # Long content
        async def mock_get_page_content(*args, **kwargs):
            return mock_content
        cli.agent.get_page_content = mock_get_page_content
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("browser: example.com")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert "..." in printed_text
            assert len(printed_text) < len(mock_content)

    @pytest.mark.asyncio
    async def test_interactive_mode(self, cli):
        """Test interactive mode with various commands."""
        mock_inputs = ["help", "search: python", "exit"]
        mock_response = "Assistant response"
        mock_results = []
        
        async def mock_process_message(*args, **kwargs):
            return mock_response
        async def mock_search(*args, **kwargs):
            return mock_results
            
        cli.agent.process_message = mock_process_message
        cli.agent.search = mock_search
        
        with patch('builtins.input', side_effect=mock_inputs), \
             patch('builtins.print') as mock_print:
            await cli.interactive_mode()
            
            # Verify help was shown
            help_calls = [call for call in mock_print.call_args_list 
                         if "Available commands:" in str(call)]
            assert len(help_calls) > 0
            
            # Verify goodbye message
            goodbye_calls = [call for call in mock_print.call_args_list 
                           if "Goodbye!" in str(call)]
            assert len(goodbye_calls) > 0

    def test_show_help(self, cli):
        """Test help message display."""
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            cli._show_help()
            output = captured_output.getvalue()
            
            # Verify help message contains key information
            assert "Available commands:" in output
            assert "search:" in output
            assert "http:" in output
            assert "browser:" in output
            assert "help" in output
            assert "exit" in output
        finally:
            sys.stdout = sys.__stdout__

    @pytest.mark.asyncio
    async def test_process_single_message_search_error(self, cli):
        """Test error handling in search command."""
        async def mock_search(*args, **kwargs):
            raise Exception("Search failed")
        cli.agent.search = mock_search
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("search: python")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert "Error" in printed_text
            assert "Search failed" in printed_text

    @pytest.mark.asyncio
    async def test_process_single_message_browser_error(self, cli):
        """Test error handling in browser command."""
        async def mock_get_page_content(*args, **kwargs):
            raise Exception("Browser failed")
        cli.agent.get_page_content = mock_get_page_content
        
        with patch('builtins.print') as mock_print:
            await cli.process_single_message("browser: example.com")
            printed_text = "".join(str(call) for call in mock_print.call_args_list)
            assert "Error" in printed_text
            assert "Browser failed" in printed_text

    @pytest.mark.asyncio
    async def test_interactive_mode_keyboard_interrupt(self, cli):
        """Test handling of KeyboardInterrupt in interactive mode."""
        with patch('builtins.input', side_effect=KeyboardInterrupt), \
             patch('builtins.print') as mock_print:
            await cli.interactive_mode()
            mock_print.assert_called_with("\nGoodbye!") 

    @pytest.mark.asyncio
    async def test_interactive_mode_empty_message(self, cli, capsys):
        # Mock input to return empty string then 'exit'
        with patch('builtins.input', side_effect=['', 'exit']):
            await cli.interactive_mode()
        
        captured = capsys.readouterr()
        assert 'Goodbye!' in captured.out

    @pytest.mark.asyncio
    async def test_interactive_mode_help_command(self, cli, capsys):
        # Mock input to return 'help' then 'exit'
        with patch('builtins.input', side_effect=['help', 'exit']):
            await cli.interactive_mode()
        
        captured = capsys.readouterr()
        assert 'Available commands:' in captured.out
        assert 'search:' in captured.out
        assert 'http:' in captured.out
        assert 'browser:' in captured.out
        assert 'help' in captured.out
        assert 'exit' in captured.out

    @pytest.mark.asyncio
    async def test_interactive_mode_error(self, cli, capsys):
        # Mock process_single_message to raise an exception
        cli.process_single_message = AsyncMock(side_effect=Exception('Test error'))
        
        # Mock input to return a message then 'exit'
        with patch('builtins.input', side_effect=['test message', 'exit']):
            await cli.interactive_mode()
        
        captured = capsys.readouterr()
        assert 'Error: Test error' in captured.out 