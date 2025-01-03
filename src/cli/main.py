"""Main CLI module."""
import asyncio
import logging
from typing import List, Optional
from src.agent.base import Agent
from src.cli.handlers.search import SearchHandler
from src.cli.handlers.http import HttpHandler
from src.cli.handlers.browser import BrowserHandler
from src.cli.handlers.base import BaseHandler

logger = logging.getLogger(__name__)

class AgentCLI:
    """Command-line interface for the AI agent."""

    def __init__(self):
        """Initialize the CLI with an agent and command handlers."""
        logger.info("Initializing AgentCLI")
        self.agent = Agent()
        self.handlers: List[BaseHandler] = [
            SearchHandler(self.agent),
            HttpHandler(self.agent),
            BrowserHandler(self.agent)
        ]

    async def process_single_message(self, message: str):
        """Process a single message in non-interactive mode."""
        logger.info(f"Processing single message: {message}")

        # Try handlers first
        for handler in self.handlers:
            if handler.can_handle(message):
                result = await handler.handle(message)
                if isinstance(handler, SearchHandler):
                    print(handler.format_results(result))
                elif isinstance(handler, HttpHandler):
                    print(handler.format_result(result))
                elif isinstance(handler, BrowserHandler):
                    print(handler.format_result(result))
                return

        # If no handler matched, treat as chat
        response = await self.agent.process_message(message)
        print(f"\nAssistant: {response}")

    async def interactive_mode(self):
        """Run the CLI in interactive mode."""
        print("\nAI Agent CLI")
        print("===========")
        self._show_help()

        try:
            while True:
                message = input("\nYou: ").strip()
                
                if not message:
                    continue
                    
                if message.lower() == "exit":
                    print("\nGoodbye!")
                    break
                    
                if message.lower() == "help":
                    self._show_help()
                    continue
                
                await self.process_single_message(message)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            logger.error(f"Error in interactive mode: {str(e)}")
            print(f"\nError: {str(e)}")

    def _show_help(self):
        """Show help information."""
        print("\nAvailable commands:")
        print("  search: <query>     - Search the web")
        print("  http: <url>         - Make an HTTP request")
        print("  browser: <url>      - Get content from a webpage")
        print("  help                - Show this help message")
        print("  exit                - Exit the program")
        print("\nOr just type your message to chat with the AI assistant.")

if __name__ == "__main__":
    cli = AgentCLI()
    asyncio.run(cli.interactive_mode()) 