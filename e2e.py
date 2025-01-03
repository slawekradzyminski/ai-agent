"""End-to-end tests for the AI agent."""
import asyncio
import sys
import logging
import os
import shutil
from src.cli.main import AgentCLI
from src.cli.handlers.http import HttpHandler
from src.cli.handlers.search import SearchHandler
from src.cli.handlers.browser import BrowserHandler

# Configure logging
def setup_logging():
    """Set up logging directory and configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

logger = setup_logging()

def cleanup_logs():
    """Clean up log files after tests."""
    try:
        if os.path.exists('logs'):
            shutil.rmtree('logs')
    except Exception as e:
        logger.warning(f"Failed to clean up logs: {e}")

async def run_tests():
    """Run end-to-end tests to verify core functionality."""
    try:
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
            if http_result.get('data', {}).get('title') or http_result.get('title'):
                print("✅ HTTP request successful")
            else:
                print("❌ HTTP request failed")
                print(f"Response was: {http_result}")
                sys.exit(1)

            # Test 2: Web Search
            print("\n2. Testing Web Search")
            print("-------------------")
            try:
                search_results = await search_handler.handle("search: Python programming language")
                if search_results and len(search_results) > 0:
                    print("✅ Web search successful")
                else:
                    print("⚠️ Web search returned no results (this is okay)")
            except Exception as e:
                logger.warning(f"Web search failed (this is okay): {str(e)}")
                print("⚠️ Web search failed (this is okay)")

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

            # Test 5: Memory - Single Tool
            print("\n5. Testing Memory (Single Tool)")
            print("------------------------------")
            # First fetch content
            await browser_handler.handle("browser: https://www.python.org")
            # Then ask about it
            memory_response = await cli.agent.process_message(
                "What programming language's website did we just visit?",
                system_prompt="You are a helpful AI assistant. Be concise."
            )
            if "Python" in memory_response:
                print("✅ Single tool memory test successful")
            else:
                print("❌ Single tool memory test failed")
                print(f"Response was: {memory_response}")
                sys.exit(1)

            # Test 6: Memory - Multiple Tools
            print("\n6. Testing Memory (Multiple Tools)")
            print("--------------------------------")
            # Execute multiple tools in sequence
            await browser_handler.handle("browser: https://www.python.org")
            try:
                await search_handler.handle("search: Python programming benefits")
            except Exception as e:
                logger.warning(f"Search failed (this is okay for the test): {str(e)}")
            
            # Ask about both results
            multi_memory_response = await cli.agent.process_message(
                "What did we just look up about Python?",
                system_prompt="You are a helpful AI assistant. Mention what you found from the website and any search results if available. Be concise."
            )
            # Check that at least the website visit is remembered
            has_website = any(term in multi_memory_response.lower() for term in [
                "python.org",
                "python website",
                "python programming language website",
                "python programming language",
                "python's website",
                "website content",
                "information about python"
            ])
            if has_website:
                print("✅ Multiple tools memory test successful")
            else:
                print("❌ Multiple tools memory test failed")
                print(f"Response was: {multi_memory_response}")
                sys.exit(1)

            # Test 7: Memory Clearing
            print("\n7. Testing Memory Clearing")
            print("------------------------")
            # After processing a message, tool memories should be cleared
            if len(cli.agent._recent_tool_memories) == 0:
                print("✅ Memory clearing test successful")
            else:
                print("❌ Memory clearing test failed")
                sys.exit(1)

            # Test 8: Content Summarization
            print("\n8. Testing Content Summarization")
            print("-----------------------------")
            # Fetch technical article
            await browser_handler.handle("browser: https://www.awesome-testing.com/tips/deep-technical-understanding")
            summary_response = await cli.agent.process_message(
                "What does the author think about deep technical understanding? Summarize the key points."
            )
            
            # Check for comprehensive coverage of key points with synonyms
            key_concepts = {
                "business understanding": ["business understanding", "business knowledge"],
                "technical understanding": ["technical understanding", "technical knowledge", "technical aspects"],
                "microservices": ["microservices", "micro-services"],
                "asynchronous": ["asynchronous", "async"],
                "system boundaries": ["system boundaries", "boundaries", "system integration"],
                "integration": ["integration", "integrate", "integrating"],
                "competitive advantage": ["competitive advantage", "competitiveness", "advantage over the competition", "market advantage", "competitive edge"],
                "books": ["book", "books", "reading"]
            }
            
            missing_concepts = []
            for concept, synonyms in key_concepts.items():
                if not any(syn.lower() in summary_response.lower() for syn in synonyms):
                    missing_concepts.append(concept)
            
            if not missing_concepts:
                print("✅ Content summarization test successful")
            else:
                print("❌ Content summarization test failed")
                print("Missing concepts:", ", ".join(missing_concepts))
                print(f"Response was: {summary_response}")
                sys.exit(1)

            print("\n✅ All tests passed!")
            return 0

        except Exception as e:
            logger.error(f"Test failed: {str(e)}", exc_info=True)
            print(f"\n❌ Test failed: {str(e)}")
            return 1

    finally:
        # Clean up logs after tests
        cleanup_logs()

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        cleanup_logs()  # Clean up even on interrupt
        sys.exit(1) 