"""Main CLI module."""
import os
import sys
import asyncio
import logging
from typing import Dict
from dotenv import load_dotenv
from src.agent.base import Agent
from src.cli.handlers.base import BaseHandler
from src.cli.handlers import SearchHandler, HttpHandler, BrowserHandler, MemoryHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLI:
    """Command-line interface for the AI agent."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.agent = Agent(openai_api_key=os.getenv("OPENAI_API_KEY", ""))
        self.handlers: Dict[str, BaseHandler] = {
            "memory": MemoryHandler(self.agent),
            "search": SearchHandler(self.agent),
            "http": HttpHandler(self.agent),
            "browser": BrowserHandler(self.agent)
        }
        
    def get_help(self) -> str:
        """Get help text."""
        help_text = "Available commands:\n"
        help_text += "- help: Show this help message\n"
        help_text += "- exit: Exit the program\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
        
    async def process_command(self, command: str) -> str:
        """Process a command and return the result."""
        if command == "help":
            return self.get_help()
        elif command == "exit":
            sys.exit(0)
        
        # Find the appropriate handler
        for prefix, handler in self.handlers.items():
            if handler.can_handle(command):
                result = await handler.handle(command)
                if hasattr(handler, 'format_result'):
                    return handler.format_result(result)
                elif hasattr(handler, 'format_results'):
                    return handler.format_results(result)
                return str(result)
                
        # If no handler found, treat as a chat message
        return await self.agent.process_message(command)

async def main():
    """Main entry point."""
    cli = CLI()
    print("AI Agent CLI")
    print('Type "help" for available commands or "exit" to quit\n')
    
    while True:
        try:
            command = input("\nYou: ").strip()
            if not command:
                continue
                
            result = await cli.process_command(command)
            print("\nAgent:", result)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 