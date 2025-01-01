"""Main CLI module for the AI agent."""
import argparse
import asyncio
import logging
import sys
from typing import List

from src.agent.base import Agent
from src.cli.handlers.search import SearchHandler
from src.cli.handlers.http import HttpHandler
from src.cli.handlers.browser import BrowserHandler
from src.config.settings import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentCLI:
    """Command-line interface for interacting with the AI agent."""

    def __init__(self):
        """Initialize the CLI with an agent instance and handlers."""
        logger.info("Initializing AgentCLI")
        self.agent = Agent()
        self.handlers = [
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
                    print(handler.format_results(message[7:].strip(), result))
                elif isinstance(handler, HttpHandler):
                    print(handler.format_result(result))
                elif isinstance(handler, BrowserHandler):
                    print(handler.format_result(message[8:].strip(), result))
                return

        # If no handler matches, process as chat message
        response = await self.agent.process_message(
            message,
            system_prompt="You are a helpful AI assistant. Be concise and informative."
        )
        print(f"\nAssistant: {response}")

    async def interactive_mode(self):
        """Run the agent in interactive mode with continuous conversation."""
        logger.info("Starting interactive mode")
        self._show_welcome_message()

        while True:
            try:
                user_input = input("\nYou: ").strip()
                logger.debug(f"Received user input: {user_input}")

                if user_input.lower() in ['exit', 'quit']:
                    logger.info("User requested exit")
                    print("\nGoodbye!")
                    break

                if user_input.lower() == 'help':
                    self._show_help()
                    continue

                await self.process_single_message(user_input)

            except Exception as e:
                logger.error(f"Error processing input: {str(e)}", exc_info=True)
                print(f"\nError: {str(e)}")

    def _show_welcome_message(self):
        """Display welcome message and instructions."""
        print("\nAI Agent Interactive Mode")
        print("------------------------")
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'search: your query' to perform a web search")
        print("Type 'http: url' to make an HTTP request")
        print("Type 'browser: url' to get page content using Chrome")
        print("Type 'help' for more information")
        print("------------------------\n")

    def _show_help(self):
        """Display help information."""
        print("\nAvailable commands:")
        print("  search: <query>  - Search the web")
        print("  http: <url>      - Make an HTTP request to a URL")
        print("  browser: <url>   - Get page content using Chrome")
        print("  help            - Display this help message")
        print("  exit            - Exit the program")
        print("  <message>       - Chat with the agent\n")


def main():
    """Main entry point for the CLI."""
    logger.info("Starting AI Agent CLI")
    parser = argparse.ArgumentParser(description="AI Agent Command Line Interface")
    parser.add_argument(
        "--message", "-m",
        help="Single message to send to the agent (non-interactive mode)"
    )
    
    args = parser.parse_args()
    cli = AgentCLI()

    try:
        if args.message:
            logger.info(f"Running in single message mode with: {args.message}")
            asyncio.run(cli.process_single_message(args.message))
        else:
            logger.info("Running in interactive mode")
            asyncio.run(cli.interactive_mode())
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1) 