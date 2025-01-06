from src.cli.handlers.base import BaseHandler

class MemoryHandler(BaseHandler):
    def can_handle(self, command: str) -> bool:
        return command.startswith("memory")
    
    async def handle(self, command: str) -> str:
        if command == "memory documents":
            return "Stored documents:\n" + "\n".join(self.agent.memory._documents)
        elif command == "memory metadata":
            return "Document metadata:\n" + "\n".join(str(m) for m in self.agent.memory._metadatas)
        elif command == "memory tools":
            return "Tool outputs:\n" + "\n".join(str(t) for t in self.agent.memory._tool_outputs)
        elif command == "memory messages":
            return "Conversation messages:\n" + "\n".join(str(m.content) for m in self.agent.memory._messages)
        elif command.startswith("memory search "):
            query = command[len("memory search "):]
            results = await self.agent.memory.get_relevant_tool_outputs(query)
            return "Search results:\n" + "\n".join(str(r) for r in results)
        else:
            return self.get_help()
    
    def get_help(self) -> str:
        return """Memory inspection commands:
- memory documents: Show all stored documents
- memory metadata: Show metadata for all documents
- memory tools: Show all tool outputs
- memory messages: Show conversation messages
- memory search <query>: Search memory with a query""" 