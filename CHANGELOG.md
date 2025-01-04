# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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