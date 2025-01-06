# AI Agent

An AI agent with web search and HTTP request capabilities, built with LangChain and OpenAI.

## Features

- Autonomous tool selection and execution based on context
- Vector-based memory system with semantic search capabilities
- Chat interaction using OpenAI's language models
- Web search using DuckDuckGo
- HTTP requests to fetch web content
- Browser-based web scraping with Chrome
- Interactive command-line interface
- Advanced conversation history with LangChain's latest patterns
- Modular command handling system
- Comprehensive logging system with:
  - Request/response tracking
  - Token usage monitoring
  - Error logging
  - Monthly log rotation
  - Proper message formatting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-agent.git
cd ai-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Interactive Mode

Start the interactive CLI:
```bash
python -m src.cli.main
```

Available commands:
- `search <query>` or `search: <query>` - Search the web
- `http <url>` or `http: <url>` - Make an HTTP request
- `browser <url>` or `browser: <url>` - Browse a webpage
- `memory documents` - Show stored documents
- `memory metadata` - Show document metadata
- `memory tools` - Show tool outputs
- `memory messages` - Show conversation messages
- `memory search <query>` - Search memory with semantic search
- `help` - Show help message
- `exit` - Exit the program

Or just type your message to chat with the agent.

### Logs

Logs are stored in the `logs` directory with monthly rotation:
- `logs/requests_YYYYMM.log` - OpenAI API requests and responses
- Each log file is limited to 10MB with backup rotation
- Logs include:
  - Request details (ID, model, temperature, messages)
  - Response content and token usage
  - Error details when things go wrong
  - Proper formatting of system and human messages

## Project Structure

- `src/` - Source code
  - `agent/` - Agent implementation
    - `base.py` - Core agent with autonomous tool selection
  - `callbacks/` - Callback handlers
    - `openai_logger.py` - OpenAI request logging
    - `tool_output.py` - Tool usage logging
  - `cli/` - Command-line interface
    - `handlers/` - Command handlers
      - `base.py` - Base handler class
      - `search.py` - Search command handler
      - `http.py` - HTTP command handler
      - `browser.py` - Browser command handler
      - `memory.py` - Memory inspection handler
    - `main.py` - Main CLI entry point
  - `tools/` - Tool implementations (search, HTTP, browser)
  - `memory/` - Memory and chat history management
    - `vector_memory.py` - Vector-based memory implementation
  - `config/` - Configuration management
    - `logging_config.py` - Logging configuration
- `tests/` - Test suite
  - `callbacks/` - Callback tests
  - `cli/` - CLI-specific tests
  - `context/` - Context building tests
  - `test_agent.py` - Agent tests
  - `test_agent_memory.py` - Memory system tests
- `e2e.py` - End-to-end tests

## Key Components

### Agent

The agent uses LangChain's latest patterns for:
- Autonomous tool selection based on context
- Advanced conversation history management
- Proper message type handling
- Error handling and logging
- Intelligent context building for responses

### Memory System

Uses vector-based memory with TF-IDF and cosine similarity:
- Semantic search for relevant context retrieval
- Efficient document and metadata storage
- Tool output tracking and retrieval
- Conversation history management
- Context-aware response generation

### Logging System

Comprehensive logging of all OpenAI interactions:
- Request/response correlation with unique IDs
- Token usage tracking
- Error logging with stack traces
- Monthly log rotation with size limits
- Proper message formatting and indentation

### Tools

- `web_search`: DuckDuckGo search integration
- `http_request`: HTTP request handling
- `browser`: Chrome-based web scraping

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Versioning

This project follows [Semantic Versioning](https://semver.org/). See [CHANGELOG.md](CHANGELOG.md) for version details.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 