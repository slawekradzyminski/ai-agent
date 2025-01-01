# AI Agent

An autonomous agent built with LangChain framework, capable of performing web searches and interacting through a command-line interface.

## Features

- 🔍 DuckDuckGo search integration
- 🤖 OpenAI GPT integration
- 💻 Interactive command-line interface
- ⚡ Async support
- 🔐 Secure environment configuration

## Prerequisites

- Python 3.9 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/slawekradzyminski/ai-agent.git
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

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Interactive Mode

Start the interactive CLI mode:
```bash
python -m src.cli
```

In interactive mode, you can:
- Chat with the AI agent
- Perform web searches
- Get help with commands

Available commands:
- `search: query` - Search the web using DuckDuckGo
- `help` - Show available commands
- `exit` or `quit` - End the session

Example search:
```bash
You: search: World Cup 2024
```

### Single Message Mode

Send a single message or search query:
```bash
python -m src.cli -m "your message here"
python -m src.cli -m "search: your search query"
```

Examples:
```bash
# Chat with the agent
python -m src.cli -m "What is artificial intelligence?"

# Perform a search
python -m src.cli -m "search: latest AI developments"
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific test files:
```bash
python -m pytest tests/test_cli.py
python -m pytest tests/test_tools.py
```

### End-to-End Tests

Run the standalone e2e test to verify search functionality:
```bash
python e2e.py
```

This will:
- Perform a real search for awesome-testing.com
- Verify that the blog is found in the results
- Display detailed test results with emojis
- Exit with code 0 on success, 1 on failure

## Project Structure

- `src/` - Source code
  - `agent/` - Agent implementation
  - `tools/` - Tool integrations (e.g., search)
  - `config/` - Configuration management
  - `cli.py` - Command-line interface
- `tests/` - Test files
- `e2e.py` - Standalone end-to-end tests
- `.env.example` - Environment variables template
- `requirements.txt` - Project dependencies

## Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Update CHANGELOG.md with changes

## License

This project is licensed under the MIT License - see the LICENSE file for details. 