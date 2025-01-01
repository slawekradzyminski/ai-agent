"""End-to-end tests for the AI agent that can be run directly."""
import asyncio
import sys
from src.cli import AgentCLI


async def test_search_awesome_testing():
    """
    End-to-end test verifying that searching for awesome-testing.com returns the blog.
    This test makes actual API calls.
    """
    print("Running end-to-end test for awesome-testing.com search...")
    cli = AgentCLI()
    results = cli.agent.search("awesome-testing.com")
    
    # Verify we got some results
    if not isinstance(results, list):
        print("❌ Error: Results are not in list format")
        return False
    
    if len(results) == 0:
        print("❌ Error: No search results returned")
        return False
    
    # Verify that awesome-testing.com is in the results
    found_blog = False
    for result in results:
        if 'awesome-testing.com' in result.get('link', '').lower():
            found_blog = True
            print(f"✅ Found blog: {result['title']}")
            print(f"   Link: {result['link']}")
            if 'snippet' in result:
                print(f"   Snippet: {result['snippet']}")
            break
    
    if not found_blog:
        print("❌ Error: awesome-testing.com was not found in search results")
        return False
    
    print("✅ All tests passed successfully!")
    return True


def main():
    """Run the e2e tests."""
    try:
        success = asyncio.run(test_search_awesome_testing())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 