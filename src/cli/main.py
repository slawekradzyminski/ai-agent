"""Command line interface for the AI agent."""
import sys
import logging
import asyncio
from typing import Optional
from src.agent.base import Agent
from src.cli.handlers import SearchHandler, HttpHandler, BrowserHandler
from src.config.settings import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class AgentCLI:
    """Command line interface for interacting with the AI agent."""
    
    def __init__(self):
        """Initialize the CLI with handlers."""
        if not OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY is not set in settings.py or .env file")
            sys.exit(1)
            
        self.agent = Agent(openai_api_key=OPENAI_API_KEY)
        self.handlers = [
            SearchHandler(self.agent),
            HttpHandler(self.agent),
            BrowserHandler(self.agent)
        ]

    def show_help(self):
        """Show help message."""
        print("\nAvailable commands:")
        print("  search <query> - Search the web")
        print("  http <url> - Make an HTTP request")
        print("  browser <url> - Browse a webpage")
        print("  help - Show this help message")
        print("  exit - Exit the program")
        print("\nOr just type your message to chat with the agent.\n")

    async def process_single_message(self, message: str) -> Optional[str]:
        """Process a single message and return the response."""
        try:
            # Check for special commands
            if message.lower() == "help":
                self.show_help()
                return None
                
            if message.lower() == "exit":
                return "exit"
            
            # Try each handler
            for handler in self.handlers:
                if handler.can_handle(message):
                    return await handler.handle(message)
            
            # If no handler matches, treat as chat
            return await self.agent.process_message(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"An error occurred: {str(e)}"

    async def interactive_mode(self):
        """Run the CLI in interactive mode."""
        print("AI Agent CLI")
        print('Type "help" for available commands or "exit" to quit')
        
        while True:
            try:
                message = input("\nYou: ").strip()
                
                if not message:
                    continue
                    
                response = await self.process_single_message(message)
                
                if response == "exit":
                    break
                    
                if response:
                    print(f"\nAgent: {response}")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {str(e)}")
                print(f"\nAn error occurred: {str(e)}")

def main():
    """Main entry point."""
    cli = AgentCLI()
    asyncio.run(cli.interactive_mode())

if __name__ == "__main__":
    main() 