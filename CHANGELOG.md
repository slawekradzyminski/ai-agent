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
- Improved error handling and response formatting for HTTP requests
- Improved HTTP request tool with better HTML parsing
- Enhanced anti-bot handling for web scraping
- Added support for extracting content from e-commerce sites

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
- Fixed HTML content extraction from complex web pages
- Improved meta tag parsing and content selection

### Security
- Added .env to .gitignore to prevent exposure of API keys 