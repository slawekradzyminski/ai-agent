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

### Changed
- Updated all dependencies to their latest stable versions
- Resolved dependency conflicts between langchain packages
- Improved DuckDuckGo search result parsing
- Updated imports to use langchain-community and langchain-openai packages

### Deprecated
- None

### Removed
- None

### Fixed
- Fixed package version conflicts
- Fixed import paths for proper package structure
- Fixed DuckDuckGo search result parsing

### Security
- Added .env to .gitignore to prevent exposure of API keys 