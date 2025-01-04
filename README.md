# AI Agent

An AI agent with web search and HTTP request capabilities, built with LangChain and OpenAI.

## Features

- Chat interaction using OpenAI's language models
- Web search using DuckDuckGo
- HTTP requests to fetch web content
- Browser-based web scraping with Chrome
- Interactive command-line interface
- Advanced conversation history with LangChain's latest patterns
- Modular command handling system
- Autonomous tool selection based on context
- Proper error handling and logging

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
- `search: query` - Search the web using DuckDuckGo
- `http: url` - Make an HTTP request to a URL
- `browser: url` - Get page content using Chrome
- `help` - Show help message
- `exit` - Exit the program
- Any other text - Chat with the AI agent

### Single Message Mode

Send a single message:
```bash
python src/cli/main.py -m "your message here"
```

### Examples

1. Web Search:
```
You: search: Python programming best practices
```

2. HTTP Request:
```
You: http: https://api.example.com/data
```

3. Browser Content:
```
You: browser: https://example.com
```

4. Chat:
```
You: What is the capital of France?
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run end-to-end tests:
```bash
python e2e.py
```

## Project Structure

- `src/` - Source code
  - `agent/` - Agent implementation
    - `base.py` - Core agent with autonomous tool selection
  - `cli/` - Command-line interface
    - `handlers/` - Command handlers
      - `base.py` - Base handler class
      - `search.py` - Search command handler
      - `http.py` - HTTP command handler
      - `browser.py` - Browser command handler
    - `main.py` - Main CLI entry point
  - `tools/` - Tool implementations (search, HTTP, browser)
  - `memory/` - Memory and chat history management
  - `config/` - Configuration management
- `tests/` - Test suite
  - `cli/` - CLI-specific tests
  - `context/` - Context building tests
  - `test_agent.py` - Agent tests
  - `test_memory.py` - Memory system tests
- `e2e.py` - End-to-end tests

## Key Components

### Agent

The agent uses LangChain's latest patterns for:
- Autonomous tool selection based on context
- Advanced conversation history management
- Proper message type handling
- Error handling and logging

### Memory System

Uses LangChain's latest memory patterns:
- Custom `ChatMessageHistory` implementation
- Proper message type handling with `HumanMessage` and `AIMessage`
- Efficient conversation history management

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