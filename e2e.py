"""End-to-end test for the AI agent."""
import sys
from src.cli import AgentCLI

def run_tests():
    """Run end-to-end tests."""
    print("Running end-to-end tests...")
    
    # Initialize CLI
    cli = AgentCLI()
    
    # Test search functionality
    print("\nTesting search functionality...")
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
    
    # Test browser functionality
    print("\nTesting browser functionality...")
    test_url = "https://www.awesome-testing.com/2024/12/from-live-suggestions-to-agents-exploring-ai-powered-ides"
    expected_text = """AI-powered IDEs are reshaping how we approach software development, combining speed, efficiency, and contextual awareness to create smarter workflows. From live suggestions and RAG integration to chat-based support and agents, these tools are designed to enhance every stage of the development process. We are entering the era of AI-Driven Development."""
    
    try:
        content = cli.agent.get_page_content(test_url)
        if expected_text in content:
            print("✅ Successfully found expected text in page content")
        else:
            print("❌ Expected text not found in page content")
            print("\nActual content snippet:")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error accessing page: {str(e)}")
        sys.exit(1)

    print("\n✅ All tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    run_tests() 