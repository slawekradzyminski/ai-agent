# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2025-01-08

### Added
- New `OpenAICallbackHandler` for comprehensive OpenAI request logging
- Detailed logging of all OpenAI requests, responses, and errors
- Integration with existing logging system using INFO level
- Request-response correlation through unique IDs
- Token usage tracking in logs
- Proper message formatting with indentation and newline handling
- Improved error handling with detailed error logs
- Monthly log rotation with 10MB size limit

### Changed
- Updated agent to use both tool output and OpenAI logging callbacks
- Enhanced logging format for better readability
- Improved error handling with detailed error logs
- Better handling of system and human messages in logs
- More robust model name extraction from various sources

## [0.5.0] - 2025-01-07

### Added
- New `ToolOutputCallbackHandler` to capture and store tool outputs during autonomous agent usage
- Enhanced logging in HTTP and Browser tools for better debugging
- Improved error handling in browser and HTTP request operations

### Changed
- Modified `Agent` class to integrate tool output storage functionality
- Updated test suite with new tests for callback handlers and tool output storage
- Enhanced browser and HTTP tools with better error handling and logging

### Fixed
- Tool outputs are now properly stored in vector memory during autonomous agent usage
- Improved handling of browser and HTTP requests with better error reporting

## [0.4.0] - 2025-01-06

### Added
- New `VectorMemory` implementation using TF-IDF and cosine similarity for semantic search
- Memory inspection commands in CLI (`memory documents`, `memory metadata`, `memory tools`, `memory messages`, `memory search`)
- Support for both space and colon command formats (e.g., `search query` or `search: query`)

### Changed
- Migrated from basic memory to vector-based memory system
- Improved command handling with better separation of concerns
- Enhanced test coverage for memory and CLI components
- Unified command format handling across all handlers

### Removed
- Old memory implementation and its tests
- Deprecated memory patterns and unused code

## [0.3.0] - 2025-01-05

### Changed
- Enhanced agent autonomy with improved tool selection and execution
- Fixed memory implementation to correctly store and retrieve conversation history
- Improved context building for more coherent responses
- Updated tool integration for better error handling

### Added
- Proper tool output storage in memory
- Enhanced conversation context management
- Better integration between agent and memory systems

## [0.2.0] - 2025-01-04

### Changed
- Migrated memory system to use latest LangChain patterns
- Replaced deprecated `ConversationBufferMemory` with custom `ChatMessageHistory`
- Updated agent executor to use `ainvoke` instead of deprecated `arun`
- Improved chat history handling with proper message types
- Fixed all tests to match new memory implementation

### Added
- New `ChatMessageHistory` class implementing `BaseChatMessageHistory`
- Better message type handling with `HumanMessage` and `AIMessage`
- Improved error handling and logging

### Removed
- Deprecated memory components and patterns
- Legacy conversation buffer implementation

## [0.1.0] - 2025-01-03

### Added
- Initial release
- Chat interaction using OpenAI's language models
- Web search using DuckDuckGo
- HTTP requests to fetch web content
- Browser-based web scraping with Chrome
- Interactive command-line interface
- Conversation history tracking
- Modular command handling system 