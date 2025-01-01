"""End-to-end test for the AI agent."""
import sys
from src.cli import AgentCLI

def run_tests():
    """Run end-to-end tests."""
    print("Running end-to-end test for awesome-testing.com search...")
    
    # Initialize CLI
    cli = AgentCLI()
    
    # Test search functionality
    results = cli.agent.search("awesome-testing.com")
    
    # Check if the blog is in the results
    blog_found = False
    blog_url = None
    
    for result in results:
        if "awesome-testing.com" in result.get("link", "").lower():
            blog_found = True
            blog_url = result.get("link")
            print(f"✅ Found blog: {result.get('title', 'No title')}")
            print(f"   Link: {blog_url}")
            print(f"   Snippet: {result.get('snippet', '')[:50]}...")
            break
    
    if not blog_found:
        print("❌ Blog not found in search results")
        sys.exit(1)
    
    # Test HTTP request functionality
    print("\nTesting HTTP request functionality on the blog...")
    try:
        response = cli.agent.http_request(blog_url)
        if response and ("content" in response or "text" in response):
            print("✅ Successfully fetched blog content")
            content = response.get("content", response.get("text", ""))
            if isinstance(content, str) and len(content) > 0:
                print(f"✅ Successfully retrieved {len(content)} characters of content")
            else:
                print("❌ Invalid or empty content")
                sys.exit(1)
        else:
            print("❌ Failed to fetch blog content")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    run_tests() 