"""Command-line interface for the AI agent."""
import argparse
import asyncio
import logging
import sys
from typing import Optional, List, Dict, Any

from src.agent.base import Agent
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
        """Initialize the CLI with an agent instance."""
        logger.info("Initializing AgentCLI")
        self.agent = Agent()

    async def process_single_message(self, message: str):
        """Process a single message in non-interactive mode."""
        logger.info(f"Processing single message: {message}")
        
        # Check if it's a search command
        if message.lower().startswith('search:'):
            query = message[7:].strip()
            logger.info(f"Processing search request: {query}")
            results = self.agent.search(query)
            self._display_search_results(query, results)
        # Check if it's a http request command
        elif message.lower().startswith('http:'):
            url = message[7:].strip()
            logger.info(f"Processing http request: {url}")
            result = self.agent.http_request(url)
            self._display_http_result(result)
        else:
            # Process as normal message
            response = await self.agent.process_message(
                message,
                system_prompt="You are a helpful AI assistant. Be concise and informative."
            )
            print(f"\nAssistant: {response}")

    async def interactive_mode(self):
        """Run the agent in interactive mode with continuous conversation."""
        logger.info("Starting interactive mode")
        print("\nAI Agent Interactive Mode")
        print("------------------------")
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'search: your query' to perform a web search")
        print("Type 'http: url' to make an HTTP request")
        print("Type 'help' for more information")
        print("------------------------\n")

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                logger.debug(f"Received user input: {user_input}")

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit']:
                    logger.info("User requested exit")
                    print("\nGoodbye!")
                    break

                # Check for help command
                if user_input.lower() == 'help':
                    logger.debug("Displaying help information")
                    self._show_help()
                    continue

                # Handle search commands
                if user_input.lower().startswith('search:'):
                    query = user_input[7:].strip()
                    logger.info(f"Processing search request: {query}")
                    results = self.agent.search(query)
                    self._display_search_results(query, results)
                    continue

                # Handle http commands
                if user_input.lower().startswith('http:'):
                    url = user_input[5:].strip()
                    logger.info(f"Processing http request: {url}")
                    result = self.agent.http_request(url)
                    self._display_http_result(result)
                    continue

                # Process normal message
                logger.info("Processing chat message")
                response = await self.agent.process_message(
                    user_input,
                    system_prompt="You are a helpful AI assistant. Be concise and informative."
                )
                print(f"\nAssistant: {response}")

            except Exception as e:
                logger.error(f"Error processing input: {str(e)}", exc_info=True)
                print(f"\nError: {str(e)}")

    def _show_help(self):
        """Display help information."""
        logger.debug("Showing help information")
        print("\nAvailable Commands:")
        print("------------------")
        print("search: <query>  - Perform a web search")
        print("http: <url>      - Make an HTTP request")
        print("help            - Show this help message")
        print("exit/quit       - End the session")
        print("\nGeneral Usage:")
        print("-------------")
        print("- Type any message to chat with the AI")
        print("- Use 'search:' prefix for web searches")
        print("- Use 'http:' prefix to make HTTP requests")
        print("- The agent will remember your conversation")

    def _display_search_results(self, query: str, results: List[Dict[str, Any]]):
        """Display search results in a formatted manner."""
        logger.info(f"Displaying {len(results)} search results for query: {query}")
        
        print(f"\nSearch Results for: {query}")
        print("-" * (len(query) + 20))
        
        if not results:
            logger.warning("No search results found")
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            try:
                print(f"\n{i}. {result.get('title', 'No title')}")
                print(f"   {result.get('link', 'No link')}")
                if 'snippet' in result:
                    print(f"   {result['snippet']}")
                print(f"   Source: {result.get('source', 'unknown')}")
            except Exception as e:
                logger.error(f"Error displaying result {i}: {str(e)}")
                continue

    def _display_http_result(self, result: Dict[str, Any]):
        """Display HTTP request result in a formatted manner."""
        logger.info(f"Displaying HTTP request result for URL: {result.get('url')}")
        
        print("\nHTTP Response:")
        print("---------------")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        if result.get('url'):
            print(f"\nURL: {result['url']}")
        
        if result.get('content_type'):
            print(f"\nContent Type: {result['content_type']}")
        
        print(f"\nURL: {result.get('url')}")
        print(f"Content Type: {result.get('content_type', 'unknown')}")
        
        if result.get('content'):
            print("\nContent:")
            print("-" * 50)
            if result['content_type'] == 'json':
                import json
                print(json.dumps(result['content'], indent=2))
            else:
                print(result['content'])

    def _process_command(self, command: str) -> None:
        """Process a command and display the result."""
        if command.startswith('search:'):
            query = command[7:].strip()
            if query:
                self._display_search_results(self.agent.search(query))
            else:
                print("Please provide a search query")
        
        elif command.startswith('http:'):
            url = command[5:].strip()
            if url:
                self._display_http_result(self.agent.http_request(url))
            else:
                print("Please provide a URL")
        
        elif command == 'help':
            self._display_help()
        
        elif command == 'exit':
            self.running = False
        
        else:
            self._process_chat_message(command)

    def _display_help(self) -> None:
        """Display help information."""
        print("\nAvailable commands:")
        print("  search: <query>  - Search the web")
        print("  http: <url>      - Make an HTTP request to a URL")
        print("  help            - Display this help message")
        print("  exit            - Exit the program")
        print("  <message>       - Chat with the agent\n")

    def _display_http_result(self, result: Dict[str, Any]) -> None:
        """Display the result of an HTTP request."""
        if 'error' in result:
            print(f"\nError: {result['error']}")
            return

        print("\nHTTP Response:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print(result)


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
            # Single message mode
            logger.info(f"Running in single message mode with: {args.message}")
            asyncio.run(cli.process_single_message(args.message))
        else:
            # Interactive mode
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