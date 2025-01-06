# OpenAI Request Logging Implementation Plan

## Current State Analysis
- Project has a `logging_config.py` with `OpenAIFormatter` but it's not integrated with LangChain
- Project uses LangChain's callback system for tool outputs (`ToolOutputCallbackHandler`)
- Logging is set up but not effectively used for OpenAI requests
- Project uses latest LangChain patterns and OpenAI integration

## How It Works

### Callback System Flow
1. Agent makes an LLM call through LangChain
2. LangChain triggers `on_llm_start` callback before sending request
3. Request is sent to OpenAI
4. Response is received from OpenAI
5. LangChain triggers `on_llm_end` callback with response
6. If error occurs, `on_llm_error` callback is triggered instead

### Logging System
- Uses Python's built-in logging system
- Logs are formatted using custom `OpenAIFormatter`
- Monthly rotating files with RotatingFileHandler
- Correlation through request IDs
- Structured data logging with clear formatting

## Implementation Plan

### 1. Create OpenAI Callback Handler

Create a new file `src/callbacks/openai_logger.py`:
```python
class OpenAICallbackHandler(BaseCallbackHandler):
    """Callback handler for logging OpenAI requests and responses."""
    
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger
    
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Log when LLM starts processing."""
        self.logger.info({
            'openai_request': {
                'id': kwargs.get('invocation_params', {}).get('request_id', 'N/A'),
                'model': serialized.get('name', 'N/A'),
                'messages': prompts,
                'temperature': kwargs.get('invocation_params', {}).get('temperature', 'N/A'),
                'timestamp': datetime.now().isoformat()
            }
        })
    
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Log when LLM completes processing."""
        for generation in response.generations[0]:
            self.logger.info({
                'openai_response': {
                    'id': kwargs.get('request_id', 'N/A'),
                    'model': response.llm_output.get('model_name', 'N/A'),
                    'content': generation.text,
                    'total_tokens': response.llm_output.get('token_usage', {}).get('total_tokens', 'N/A'),
                    'completion_tokens': response.llm_output.get('token_usage', {}).get('completion_tokens', 'N/A'),
                    'prompt_tokens': response.llm_output.get('token_usage', {}).get('prompt_tokens', 'N/A'),
                    'finish_reason': generation.generation_info.get('finish_reason', 'N/A'),
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    async def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        """Log when LLM encounters an error."""
        self.logger.error({
            'openai_error': {
                'id': kwargs.get('request_id', 'N/A'),
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'timestamp': datetime.now().isoformat()
            }
        })
```

### 2. Integrate with Agent

Modify `src/agent/base.py` to use the callback:
```python
def __init__(self):
    # ... existing initialization ...
    callbacks = [
        ToolOutputCallbackHandler(self.memory),
        OpenAICallbackHandler(logging.getLogger('ai_agent'))
    ]
    self.llm = ChatOpenAI(
        callbacks=callbacks,
        # ... existing parameters ...
    )
```

### 3. Update Tests

Create `tests/callbacks/test_openai_logger.py`:
```python
@pytest.fixture
def logger():
    return logging.getLogger('test_openai')

@pytest.fixture
def callback_handler(logger):
    return OpenAICallbackHandler(logger)

@pytest.mark.asyncio
async def test_on_llm_start(callback_handler, caplog):
    caplog.set_level(logging.INFO)
    await callback_handler.on_llm_start(
        {"name": "gpt-4"},
        ["test prompt"],
        invocation_params={"request_id": "test-123", "temperature": 0.7}
    )
    assert "gpt-4" in caplog.text
    assert "test prompt" in caplog.text

# ... more test cases for on_llm_end and on_llm_error
```

### 4. Log File Structure

Logs will be stored in monthly rotating files:
- `logs/requests_YYYYMM.log`
- Each log entry will be formatted as:
  ```
  [TIMESTAMP] - ai_agent - INFO - OpenAI Request - ID: xxx
  Model: gpt-4
  Temperature: 0.7
  Messages: [...]
  Timestamp: ...
  
  [TIMESTAMP] - ai_agent - INFO - OpenAI Response - ID: xxx
  Model: gpt-4
  Content: ...
  Tokens - Total: xxx, Completion: xxx, Prompt: xxx
  Finish Reason: stop
  Timestamp: ...
  ```

### 5. Changes Required

1. Create new files:
   - `src/callbacks/openai_logger.py`
   - `tests/callbacks/test_openai_logger.py`

2. Modify existing files:
   - `src/agent/base.py` - Add callback integration
   - `src/callbacks/__init__.py` - Export new callback
   - `CHANGELOG.md` - Document new logging feature
   - `README.md` - Update logging documentation

## Implementation Notes

- All OpenAI requests will be logged at INFO level
- Errors will be logged at ERROR level
- Logs will include request ID for request-response correlation
- Token usage and costs will be tracked
- Timestamps will be in ISO format with timezone
- Monthly rotation ensures manageable file sizes
- Existing `OpenAIFormatter` will be used to format log messages

## Testing Strategy

1. Unit tests for callback handler
2. Integration tests with agent
3. Log format verification
4. Error handling tests
5. Log rotation tests
6. Performance impact tests

## Security Considerations

1. Sensitive data masking in logs
2. Log file permissions
3. Log retention policy
4. API key protection 