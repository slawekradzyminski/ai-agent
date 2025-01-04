from typing import List, Dict, Optional, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.memory import BaseMemory
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import Field, PrivateAttr

class VectorMemory(BaseMemory):
    """Memory class that uses TF-IDF and cosine similarity for retrieval."""
    
    memory_key: str = "history"
    return_messages: bool = True
    input_key: Optional[str] = None
    output_key: Optional[str] = None
    
    _vectorizer: TfidfVectorizer = PrivateAttr(default_factory=lambda: TfidfVectorizer(stop_words='english'))
    _documents: List[str] = PrivateAttr(default_factory=list)
    _metadatas: List[Dict] = PrivateAttr(default_factory=list)
    _vectors: Optional[Any] = PrivateAttr(default=None)
    _chat_memory: List[Any] = PrivateAttr(default_factory=list)

    @property
    def memory_variables(self) -> List[str]:
        """Return the memory variables."""
        return ["history", "tool_outputs"]

    def _update_vectors(self) -> None:
        """Update document vectors."""
        if not self._documents:
            self._vectors = None
            return
        self._vectors = self._vectorizer.fit_transform(self._documents)

    def _add_to_memory(self, text: str, metadata: Dict[str, Any]) -> None:
        """Add text and metadata to memory."""
        self._documents.append(text)
        self._metadatas.append(metadata)
        self._update_vectors()

    async def add_tool_memory(self, tool_name: str, input_str: str, output: str) -> None:
        """Add tool execution memory."""
        text = f"{tool_name}: {input_str} -> {output}"
        self._add_to_memory(text, {"type": "tool", "tool_name": tool_name})

    async def add_conversation_memory(self, message: str, is_user: bool) -> None:
        """Add conversation memory."""
        self._add_to_memory(message, {"type": "conversation", "is_user": is_user})
        if is_user:
            self._chat_memory.append(HumanMessage(content=message))
        else:
            self._chat_memory.append(AIMessage(content=message))

    def _search(self, query: str, k: int = 5, filter_type: Optional[str] = None) -> List[str]:
        """Search for relevant documents."""
        if not self._documents:
            return []
            
        query_vector = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self._vectors).flatten()
        
        # Get indices sorted by similarity
        indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in indices:
            if filter_type and self._metadatas[idx]["type"] != filter_type:
                continue
            results.append(self._documents[idx])
            if len(results) == k:
                break
        return results

    async def get_relevant_context(self, query: str, k: int = 5) -> List[str]:
        """Get relevant context based on query."""
        return self._search(query, k)

    async def get_relevant_tool_outputs(self, query: str, k: int = 5) -> List[Dict]:
        """Get relevant tool outputs based on query."""
        tool_outputs = self._search(query, k, filter_type="tool")
        return [self._parse_tool_output(doc) for doc in tool_outputs]

    def _parse_tool_output(self, tool_output: str) -> Dict:
        """Parse tool output string into a dictionary."""
        try:
            tool_name, rest = tool_output.split(":", 1)
            input_str, output = rest.split("->", 1)
            return {
                "tool": tool_name.strip(),
                "input": input_str.strip(),
                "output": output.strip()
            }
        except ValueError:
            return {"tool": "unknown", "input": "", "output": tool_output}

    def clear(self) -> None:
        """Clear all memory."""
        self._documents = []
        self._metadatas = []
        self._vectors = None
        self._vectorizer = TfidfVectorizer(stop_words='english')
        self._chat_memory = []

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer. Required by BaseMemory."""
        if inputs.get("input"):
            self._chat_memory.append(HumanMessage(content=inputs["input"]))
        if outputs.get("output"):
            self._chat_memory.append(AIMessage(content=outputs["output"]))

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables. Required by BaseMemory."""
        query = inputs.get("input", "")
        relevant_docs = self._search(query, k=5)
        tool_outputs = [self._parse_tool_output(doc) for doc in self._search(query, k=3, filter_type="tool")]
        
        return {
            "history": self._chat_memory[-10:] if self._chat_memory else [],  # Last 10 messages
            "tool_outputs": tool_outputs
        } 