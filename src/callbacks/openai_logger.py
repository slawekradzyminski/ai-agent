"""OpenAI callback handler for logging requests and responses."""
from typing import Any, Dict, List, Optional
from datetime import datetime
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from src.config.logging_config import get_logger

class OpenAICallbackHandler(BaseCallbackHandler):
    """Callback handler for logging OpenAI requests and responses."""
    
    def __init__(self):
        """Initialize the callback handler."""
        super().__init__()
        self.logger = get_logger('file')
    
    async def on_llm_start(
        self,
        serialized: Dict[str, Any],
        messages: List[Any],
        **kwargs: Any,
    ) -> None:
        """Log when an LLM starts processing."""
        invocation_params = kwargs.get('invocation_params', {})
        metadata = kwargs.get('metadata', {})
        
        # Extract model info from multiple possible locations
        model_name = (
            metadata.get('ls_model_name') or
            invocation_params.get('model_name') or
            invocation_params.get('model') or
            serialized.get('name') or  # Direct name in serialized
            (serialized.get('kwargs', {}).get('model_name')) or
            'N/A'
        )
        
        # Collect message data
        message_data = []
        for msg in messages:
            if isinstance(msg, BaseMessage):
                message_data.append({
                    'type': msg.type,
                    'content': msg.content
                })
            elif isinstance(msg, str):
                message_data.append({
                    'type': 'text',
                    'content': msg
                })
            else:
                message_data.append({
                    'type': 'unknown',
                    'content': str(msg)
                })
            
        self.logger.info('', extra={
            'openai_request': {
                'id': invocation_params.get('request_id', kwargs.get('request_id', 'request-' + datetime.now().strftime('%Y%m%d-%H%M%S'))),
                'model': model_name,
                'messages': message_data,
                'temperature': invocation_params.get('temperature', 0.0),
                'timestamp': datetime.now().isoformat(),
                'note': 'Empty messages list provided' if not messages else None
            }
        })
    
    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Log when an LLM ends processing."""
        try:
            generation = response.generations[0][0] if response and response.generations else None
            
            # Extract response metadata
            response_metadata = {}
            if hasattr(generation, 'message'):
                response_metadata = getattr(generation.message, 'response_metadata', {})
            elif hasattr(generation, 'generation_info'):
                response_metadata = generation.generation_info or {}
            
            # Get token usage if available
            token_usage = {}
            if hasattr(response, 'llm_output') and response.llm_output:
                token_usage = response.llm_output.get('token_usage', {})
            
            # Get content from generation
            content = ''
            if generation:
                if hasattr(generation, 'text'):
                    content = generation.text
                elif hasattr(generation, 'message'):
                    content = generation.message.content
            
            self.logger.info('', extra={
                'openai_response': {
                    'id': kwargs.get('request_id', 'N/A'),
                    'content': content,
                    'total_tokens': token_usage.get('total_tokens', 0),
                    'completion_tokens': token_usage.get('completion_tokens', 0),
                    'prompt_tokens': token_usage.get('prompt_tokens', 0),
                    'finish_reason': response_metadata.get('finish_reason', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Empty response received (None)' if response is None else 
                           'Response contains no generations' if not generation else None
                }
            })
        except Exception as e:
            self.logger.info('', extra={
                'openai_response': {
                    'id': kwargs.get('request_id', 'N/A'),
                    'content': '',
                    'finish_reason': 'error',
                    'timestamp': datetime.now().isoformat(),
                    'note': f'Error formatting response: {str(e)}'
                }
            })
    
    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Log when an LLM errors."""
        self.logger.error('', extra={
            'openai_error': {
                'id': kwargs.get('request_id', 'N/A'),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'timestamp': datetime.now().isoformat()
            }
        }) 