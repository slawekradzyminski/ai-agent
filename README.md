# AI Agent

An autonomous agent built with LangChain framework, capable of performing tasks and interacting with various tools and APIs.

## Core Objectives
1. Create an autonomous agent using LangChain framework
2. Implement tool integration capabilities (Search, HTTP, Browser)
3. Maintain modular and extensible architecture
4. Provide easy-to-use command-line interface
5. Ensure robust testing and error handling

## Technical Stack
- Python 3.9+
- LangChain framework
- OpenAI GPT integration
- DuckDuckGo search API
- Selenium for web browsing
- Testing with pytest

## Features
### Current
- [x] Chat interaction using OpenAI's language models
- [x] DuckDuckGo search integration
- [x] HTTP request capabilities
- [x] Web browsing with Selenium
- [x] Enhanced conversation memory
- [x] Interactive command-line interface
- [x] Comprehensive test suite
- [x] Modular command handling system

### Planned
- [ ] File operations
- [ ] Data analysis tools
- [ ] API endpoint for web integration
- [ ] Configuration file support

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

## Project Structure

- `src/` - Source code
  - `agent/` - Agent implementation
  - `cli/` - Command-line interface
    - `handlers/` - Command handlers
      - `base.py` - Base handler class
      - `search.py` - Search command handler
      - `http.py` - HTTP command handler
      - `browser.py` - Browser command handler
    - `main.py` - Main CLI entry point
  - `tools/` - Tool implementations (search, HTTP, browser)
  - `config/` - Configuration management
- `tests/` - Test suite
  - `cli/` - CLI-specific tests
- `e2e.py` - End-to-end tests

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run end-to-end tests:
```bash
python e2e.py
```

## Development Guidelines
1. All new features must include tests
2. Documentation must be updated with changes
3. Code must follow PEP 8 style guide
4. Security best practices must be followed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 