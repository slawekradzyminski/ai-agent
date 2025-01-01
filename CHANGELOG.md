# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup with virtual environment
- Created PROJECTSCOPE.md defining project goals and structure
- Created CHANGELOG.md for tracking project changes
- Added prompt.md for conversation initialization
- Planned integration with LangChain framework and DuckDuckGo search tool
- Created requirements.txt with specific package versions
- Added .env.example template for environment variables
- Added .gitignore file for Python projects
- Set up basic project structure with src/ and tests/ directories
- Implemented configuration management in src/config/
- Created DuckDuckGo search tool implementation
- Implemented base agent class with search capabilities
- Added async support for message processing
- Added test script (test_tools.py) to verify search and OpenAI functionality
- Successfully tested DuckDuckGo search and OpenAI integration
- Added command-line interface with interactive mode
- Added CLI tests with pytest
- Verified search functionality with specific website queries
- Created comprehensive README.md with installation and usage instructions
- Added proper logging configuration from environment settings
- Added standalone e2e test script for verifying blog search functionality
- Added HTTP request tool for making web requests
- Added tests for HTTP request functionality
- Enhanced e2e tests to verify both search and HTTP capabilities
- Implemented Selenium-based browser tool for web scraping
- Added browser command to CLI for fetching page content
- Created end-to-end tests for browser functionality
- Added Chrome WebDriver integration with headless mode
- Implemented enhanced conversation memory with RAG-like functionality
- Added tool output tracking and association with messages
- Created memory module for structured storage of conversation and tool outputs
- Added support for retrieving relevant tool outputs for context
- Added modular command handling system with base handler class
- Created separate handlers for search, HTTP, and browser commands
- Added comprehensive tests for each command handler
- Core functionality tests in `e2e.py` that verify:
  - HTTP requests using JSONPlaceholder API
  - Web search functionality
  - Browser content fetching
  - Chat interaction
- Better error handling and logging in tests
- Immediate test failure on any component failure

### Changed
- Updated all dependencies to their latest stable versions
- Resolved dependency conflicts between langchain packages
- Improved DuckDuckGo search result parsing
- Updated imports to use langchain-community and langchain-openai packages
- Added testing dependencies (pytest, pytest-asyncio, pytest-mock)
- Enhanced search result parsing and display formatting
- Improved project documentation with detailed usage examples
- Moved test_tools.py to tests directory and converted to pytest format
- Improved logging configuration with proper level handling
- Moved e2e tests to root directory for easier command-line execution
- Renamed browser functionality to HTTP request for better clarity
- Updated CLI interface to use 'http:' command
- Enhanced browser tool to handle dynamic content loading
- Updated CLI help messages to include browser command
- Improved test coverage for browser functionality
- Refactored CLI code into modular structure with separate handlers
- Moved CLI implementation to dedicated package with proper organization
- Enhanced CLI tests with better async support and mocking
- Updated README with new project structure and features
- Simplified test suite by merging smoke tests and e2e tests into a single `e2e.py` file
- Removed website-specific tests in favor of more reliable core functionality tests
- Removed obsolete `cli.py` in favor of the modular implementation in `src/cli/`
- Split handler tests into separate files for better maintainability:
  - `test_search_handler.py`
  - `test_http_handler.py`
  - `test_browser_handler.py`

### Deprecated
- None

### Removed
- None

### Fixed
- Fixed package version conflicts
- Fixed import paths for proper package structure
- Fixed DuckDuckGo search result parsing
- Fixed search result formatting for better readability
- Fixed logging level configuration in settings
- Fixed HTTP request error handling and response formatting
- Fixed e2e test to properly verify HTTP responses
- Fixed async handling in CLI command processing
- Fixed test imports after CLI restructuring

### Security
- Added .env to .gitignore to prevent exposure of API keys 