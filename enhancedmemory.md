# Enhanced Memory Management Implementation Plan

## Overview
Add vector database storage and semantic search capabilities to improve the agent's memory management and context retrieval.

## Current State
- Basic memory implementation using LangChain's memory patterns
- Chat history storage with `HumanMessage` and `AIMessage`
- Tool output storage in memory
- Simple context building

## Goals
1. Store conversation history and tool outputs in a vector database
2. Enable semantic search for relevant context retrieval
3. Improve context building with semantic similarity

## Implementation Steps

### 1. Add Vector Database Integration
- Add Chroma DB as the vector store (lightweight, easy to set up)
- Dependencies to add:
  ```
  chromadb
  sentence-transformers
  ```
- Create `VectorMemory` class extending current `Memory` class
- Implement document chunking and embedding generation

### 2. Update Memory Storage
```python
class VectorMemory(Memory):
    def __init__(self):
        super().__init__()
        self.vector_store = ChromaDB()
        self.embeddings = SentenceTransformerEmbeddings()
    
    async def add_tool_memory(self, tool_name: str, input: str, output: str):
        self.vector_store.add_texts(
            texts=[f"{tool_name}: {input} -> {output}"],
            metadatas=[{"type": "tool", "tool_name": tool_name}]
        )

    async def add_conversation_memory(self, message: str, is_user: bool):
        self.vector_store.add_texts(
            texts=[message],
            metadatas=[{"type": "conversation", "is_user": is_user}]
        )
```

### 3. Implement Semantic Search
```python
class VectorMemory(Memory):
    async def get_relevant_context(self, query: str, k: int = 5) -> List[str]:
        # Search vector DB
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
    
    async def get_relevant_tool_outputs(self, query: str) -> List[Dict]:
        results = self.vector_store.similarity_search(
            query,
            k=5,
            filter={"type": "tool"}
        )
        return [self._parse_tool_output(doc.page_content) for doc in results]
```

### 4. Update Context Building
- Modify `build_context` to use semantic search
- Implement relevance scoring based on embeddings
- Add configurable context window size

### 5. Testing Plan

#### Unit Tests
```python
@pytest.mark.asyncio
async def test_vector_memory_storage():
    memory = VectorMemory()
    await memory.add_tool_memory("search", "python", "result")
    results = await memory.get_relevant_context("python programming")
    assert len(results) > 0
    assert "python" in results[0].lower()

@pytest.mark.asyncio
async def test_semantic_search():
    memory = VectorMemory()
    await memory.add_conversation_memory("Python is great for AI", True)
    await memory.add_conversation_memory("Java is good for enterprise", True)
    results = await memory.get_relevant_context("artificial intelligence")
    assert "Python" in results[0]

@pytest.mark.asyncio
async def test_memory_persistence():
    memory = VectorMemory()
    await memory.add_tool_memory("search", "test", "result")
    memory2 = VectorMemory()  # Should load existing DB
    results = await memory2.get_relevant_context("test")
    assert len(results) > 0
```

### 6. Performance Considerations
- Implement caching for frequently accessed embeddings
- Add batch processing for multiple documents
- Configure index settings for optimal retrieval
- Monitor memory usage and response times