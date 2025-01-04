"""Tests for the CLI module."""
import io
import sys
import pytest
from unittest.mock import patch, AsyncMock, Mock
from src.cli.main import AgentCLI

class TestAgentCLI:
    """Tests for the AgentCLI class."""
    
    @pytest.fixture
    def cli(self):
        """Create a CLI instance for testing."""
        with patch('src.cli.main.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.process_message = AsyncMock()
            mock_agent.search = AsyncMock()
            mock_agent.make_http_request = AsyncMock()
            mock_agent.get_page_content = AsyncMock()
            mock_agent_class.return_value = mock_agent
            cli = AgentCLI()
            return cli
    
    @pytest.mark.asyncio
    async def test_process_single_message_search(self, cli):
        """Test processing a search command."""
        mock_results = [{"title": "Test", "link": "http://test.com"}]
        cli.agent.search.return_value = mock_results
        
        result = await cli.process_single_message("search: python")
        assert str(mock_results) in str(result)
        cli.agent.search.assert_called_once_with("python")
    
    @pytest.mark.asyncio
    async def test_process_single_message_http(self, cli):
        """Test processing an HTTP command."""
        mock_response = {
            'status_code': 200,
            'content_type': 'application/json',
            'data': {'status': 'ok'}
        }
        cli.agent.make_http_request.return_value = mock_response
        
        result = await cli.process_single_message("http: example.com")
        assert str(mock_response) in str(result)
        cli.agent.make_http_request.assert_called_once_with("example.com")
    
    @pytest.mark.asyncio
    async def test_process_single_message_browser(self, cli):
        """Test processing a browser command."""
        mock_content = "Page content"
        cli.agent.get_page_content.return_value = mock_content
        
        result = await cli.process_single_message("browser: example.com")
        assert mock_content in str(result)
        cli.agent.get_page_content.assert_called_once_with("example.com")
    
    @pytest.mark.asyncio
    async def test_process_single_message_chat(self, cli):
        """Test processing a chat message."""
        mock_response = "Assistant response"
        cli.agent.process_message.return_value = mock_response
        
        result = await cli.process_single_message("Hello")
        assert mock_response in str(result)
        cli.agent.process_message.assert_called_once_with("Hello")
    
    @pytest.mark.asyncio
    async def test_process_single_message_http_error_handling(self, cli):
        """Test HTTP error handling in message processing."""
        cli.agent.make_http_request.side_effect = Exception("Connection failed")
        
        result = await cli.process_single_message("http: example.com")
        assert "error" in str(result).lower()
        cli.agent.make_http_request.assert_called_once_with("example.com")
    
    @pytest.mark.asyncio
    async def test_process_single_message_browser_long_content(self, cli):
        """Test browser content truncation in message processing."""
        mock_content = {"content": "A" * 1000}  # Long content
        cli.agent.get_page_content.return_value = mock_content
        
        result = await cli.process_single_message("browser: example.com")
        assert str(mock_content) in str(result)
        cli.agent.get_page_content.assert_called_once_with("example.com")
    
    @pytest.mark.asyncio
    async def test_interactive_mode(self, cli):
        """Test interactive mode with various commands."""
        mock_inputs = ["help", "search: python", "exit"]
        mock_response = "Assistant response"
        mock_results = []
        
        cli.agent.process_message.return_value = mock_response
        cli.agent.search.return_value = mock_results
        
        with patch('builtins.input', side_effect=mock_inputs):
            await cli.interactive_mode()
    
    def test_show_help(self, cli):
        """Test help message display."""
        with patch('builtins.print') as mock_print:
            cli.show_help()
            assert any("Available commands" in str(call) for call in mock_print.call_args_list)
    
    @pytest.mark.asyncio
    async def test_process_single_message_search_error(self, cli):
        """Test error handling in search command."""
        cli.agent.search.side_effect = Exception("Search failed")
        
        result = await cli.process_single_message("search: python")
        assert "error" in str(result).lower()
        cli.agent.search.assert_called_once_with("python")
    
    @pytest.mark.asyncio
    async def test_process_single_message_browser_error(self, cli):
        """Test error handling in browser command."""
        cli.agent.get_page_content.side_effect = Exception("Browser failed")
        
        result = await cli.process_single_message("browser: example.com")
        assert "error" in str(result).lower()
        cli.agent.get_page_content.assert_called_once_with("example.com")
    
    @pytest.mark.asyncio
    async def test_interactive_mode_keyboard_interrupt(self, cli):
        """Test handling of KeyboardInterrupt in interactive mode."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            await cli.interactive_mode()
    
    @pytest.mark.asyncio
    async def test_interactive_mode_empty_message(self, cli):
        """Test handling of empty messages."""
        with patch('builtins.input', side_effect=['', 'exit']):
            await cli.interactive_mode()
    
    @pytest.mark.asyncio
    async def test_interactive_mode_help_command(self, cli):
        """Test help command in interactive mode."""
        with patch('builtins.input', side_effect=['help', 'exit']):
            await cli.interactive_mode()