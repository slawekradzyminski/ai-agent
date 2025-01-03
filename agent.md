# AI Agent Design

## Dynamic Context Building (RAG-like behavior)

### Overview
The agent will build context dynamically using available tools to achieve RAG-like behavior. When a user prompts for information (e.g. "Sławomir Radzymiński"), the agent will:
1. Search for relevant results 
2. Use browser/http requests to obtain detailed content
3. Include dynamically obtained content in OpenAI queries

### Agent Flow
```
User Query -> Tool Selection -> Content Retrieval -> Context Building -> OpenAI Query
```

### Implementation Strategy
1. Create new method `build_dynamic_context` in `Agent` class that will:
   - Analyze user's query to determine which tools to use
   - Use search tool first to find relevant URLs/resources
   - Use browser/http tools to fetch detailed content from those sources
   - Combine and format retrieved content into a context message
   - Include dynamic context in the OpenAI prompt

### Tool Orchestration
- Search tool: Find initial sources (e.g. blog posts, social profiles)
- Browser tool: Fetch content from web pages
- HTTP tool: Fetch data from APIs
- Results will be aggregated and filtered for relevance

### Context Management
- Store retrieved content in memory for follow-up questions
- Implement context truncation to stay within token limits
- Prioritize most relevant content when building the prompt

### Example Flow
For query "Tell me about Sławomir Radzymiński":
1. Search -> Find blog, LinkedIn, GitHub profiles
2. Browser -> Fetch content from blog posts
3. HTTP -> Get GitHub/LinkedIn data
4. Build Context -> Combine and summarize findings
5. OpenAI Query -> Generate response using dynamic context 