"""Test script for verifying tool functionality."""
import asyncio
import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.search import SearchTool
from src.agent.base import Agent


async def test_search():
    """Test the DuckDuckGo search functionality."""
    print("\nTesting DuckDuckGo Search:")
    print("-" * 50)
    
    search_tool = SearchTool()
    query = "Latest news about artificial intelligence"
    
    try:
        results = search_tool.search_web(query)
        print(f"Search Query: {query}")
        print("\nResults:")
        for idx, result in enumerate(results[:3], 1):  # Show first 3 results
            print(f"\n{idx}. {result.get('title', 'No title')}")
            print(f"   {result.get('link', 'No link')}")
            print(f"   {result.get('snippet', 'No snippet')}")
    except Exception as e:
        print(f"Search Error: {str(e)}")


async def test_agent():
    """Test the agent's message processing with OpenAI."""
    print("\nTesting Agent with OpenAI:")
    print("-" * 50)
    
    agent = Agent()
    test_message = "What are the main benefits of artificial intelligence?"
    
    try:
        response = await agent.process_message(
            test_message,
            system_prompt="You are a helpful AI assistant. Be concise and informative."
        )
        print(f"User Message: {test_message}")
        print(f"\nAgent Response:\n{response}")
    except Exception as e:
        print(f"Agent Error: {str(e)}")


async def main():
    """Run all tests."""
    print("Starting Tests...")
    
    # Test search functionality
    await test_search()
    
    # Test agent with OpenAI
    await test_agent()


if __name__ == "__main__":
    asyncio.run(main()) 