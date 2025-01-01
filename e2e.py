"""End-to-end tests for the AI agent."""
import asyncio
import sys
import logging
from src.cli.main import AgentCLI
from src.cli.handlers.http import HttpHandler
from src.cli.handlers.search import SearchHandler
from src.cli.handlers.browser import BrowserHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_tests():
    """Run end-to-end tests to verify core functionality."""
    print("\nRunning End-to-End Tests")
    print("=======================")
    
    # Initialize CLI and handlers
    cli = AgentCLI()
    http_handler = HttpHandler(cli.agent)
    search_handler = SearchHandler(cli.agent)
    browser_handler = BrowserHandler(cli.agent)
    
    try:
        # Test 1: HTTP Request
        print("\n1. Testing HTTP Request")
        print("----------------------")
        http_result = await http_handler.handle("http: https://jsonplaceholder.typicode.com/posts/1")
        if http_result.get("title"):
            print("✅ HTTP request successful")
        else:
            print("❌ HTTP request failed")
            sys.exit(1)

        # Test 2: Web Search
        print("\n2. Testing Web Search")
        print("-------------------")
        search_results = await search_handler.handle("search: Python programming language")
        if search_results and len(search_results) > 0:
            print("✅ Web search successful")
        else:
            print("❌ Web search failed")
            sys.exit(1)

        # Test 3: Browser
        print("\n3. Testing Browser")
        print("----------------")
        browser_content = await browser_handler.handle("browser: https://www.python.org")
        if len(browser_content) > 0:
            print("✅ Browser fetch successful")
        else:
            print("❌ Browser fetch failed")
            sys.exit(1)

        # Test 4: Chat
        print("\n4. Testing Chat")
        print("-------------")
        chat_response = await cli.agent.process_message(
            "What is 2+2?",
            system_prompt="You are a helpful AI assistant. Answer: The sum of 2 and 2 is 4."
        )
        if "4" in chat_response:
            print("✅ Chat response successful")
        else:
            print("❌ Chat response failed")
            sys.exit(1)

        print("\n✅ All tests passed!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1) 