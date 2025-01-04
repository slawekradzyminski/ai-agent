from typing import List, Dict, Optional, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.memory import BaseMemory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from pydantic import Field, PrivateAttr

class VectorMemory(BaseMemory):
    """Memory class that uses TF-IDF and cosine similarity for retrieval."""
    
    memory_key: str = "chat_history"
    return_messages: bool = True
    input_key: Optional[str] = None
    output_key: Optional[str] = None
    max_history: int = Field(default=10)
    
    _vectorizer: TfidfVectorizer = PrivateAttr(default_factory=lambda: TfidfVectorizer(stop_words='english'))
    _documents: List[str] = PrivateAttr(default_factory=list)
    _metadatas: List[Dict] = PrivateAttr(default_factory=list)
    _vectors: Optional[Any] = PrivateAttr(default=None)
    _messages: List[BaseMessage] = PrivateAttr(default_factory=list)
    _tool_outputs: List[Dict] = PrivateAttr(default_factory=list)

    @property
    def memory_variables(self) -> List[str]:
        """Return the memory variables."""
        return ["chat_history", "tool_history"]

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

    def add_user_message(self, message: str) -> None:
        """Add a user message to memory."""
        self._messages.append(HumanMessage(content=message))
        self._add_to_memory(message, {"type": "conversation", "is_user": True})
        self._trim_history()

    def add_ai_message(self, message: str) -> None:
        """Add an AI message to memory."""
        self._messages.append(AIMessage(content=message))
        self._add_to_memory(message, {"type": "conversation", "is_user": False})
        self._trim_history()

    def add_tool_memory(self, tool_name: str, input_str: str, output: str) -> None:
        """Add tool execution memory."""
        text = f"{tool_name}: {input_str} -> {output}"
        self._add_to_memory(text, {"type": "tool", "tool_name": tool_name})
        self._tool_outputs.append({
            "tool": tool_name,
            "input": input_str,
            "output": output
        })

    def get_conversation_context(self) -> List[BaseMessage]:
        """Get the conversation context."""
        return self._messages[-self.max_history:]

    def get_relevant_tool_outputs(self, query: str) -> List[Dict[str, Any]]:
        """Get tool outputs relevant to the query."""
        tool_outputs = self._search(query, k=3, filter_type="tool")
        return [self._parse_tool_output(doc) for doc in tool_outputs]

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

    def _trim_history(self) -> None:
        """Trim history to max_history messages."""
        if len(self._messages) > self.max_history:
            self._messages = self._messages[-self.max_history:]

    def clear(self) -> None:
        """Clear all memory."""
        self._documents = []
        self._metadatas = []
        self._vectors = None
        self._vectorizer = TfidfVectorizer(stop_words='english')
        self._messages = []
        self._tool_outputs = []

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        if "input" in inputs:
            self.add_user_message(inputs["input"])
        if "output" in outputs:
            self.add_ai_message(outputs["output"])

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables."""
        tool_outputs = self.get_relevant_tool_outputs(inputs.get("input", ""))
        tool_messages = []
        for output in tool_outputs:
            content = (
                f"Previous tool usage - {output['tool']}:\n"
                f"Input: {output['input']}\n"
                f"Output: {output['output']}"
            )
            tool_messages.append(SystemMessage(content=content))
            
        return {
            "chat_history": self.get_conversation_context(),
            "tool_history": tool_messages
        } 