"""Logging configuration for the application."""
import os
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

class OpenAIFormatter(logging.Formatter):
    """Custom formatter for OpenAI logs."""
    
    def _format_message(self, msg):
        """Format a single message with proper indentation and newline handling."""
        if isinstance(msg, dict):
            msg_type = msg.get('type', 'unknown')
            content = msg.get('content', '')
            # Handle special message types
            if msg_type.lower() == 'system':
                return f"System:\n{content}"
            elif msg_type.lower() == 'human':
                return f"Human: {content}"
            else:
                return f"{msg_type}: {content}"
        return str(msg)
    
    def format(self, record):
        if hasattr(record, 'openai_request'):
            data = record.openai_request
            # Format messages with proper handling of newlines and indentation
            formatted_messages = []
            for msg in data.get('messages', []):
                formatted_msg = self._format_message(msg)
                # Indent any newlines in the message
                formatted_msg = formatted_msg.replace('\n', '\n  ')
                formatted_messages.append(formatted_msg)
                    
            record.msg = "\n" + "="*80 + "\n" + \
                        f"OpenAI Request - ID: {data.get('id', 'N/A')}\n" + \
                        f"Model: {data.get('model', 'N/A')}\n" + \
                        f"Temperature: {data.get('temperature', 0.0)}\n" + \
                        f"Messages:\n  {'\n  '.join(formatted_messages)}"
            if data.get('timestamp'):
                record.msg += f"\nTimestamp: {data['timestamp']}"
            if data.get('note'):
                record.msg += f"\nNote: {data['note']}"
            record.msg += "\n" + "="*80
                
        elif hasattr(record, 'openai_response'):
            data = record.openai_response
            record.msg = "\n" + "-"*80 + "\n" + \
                        f"OpenAI Response - ID: {data.get('id', 'N/A')}\n" + \
                        f"Content: {data.get('content', '')}"
            
            # Only show token info if any tokens were used
            if any(data.get(k, 0) > 0 for k in ['total_tokens', 'completion_tokens', 'prompt_tokens']):
                record.msg += f"\nTokens Used:" + \
                            f"\n  Total: {data.get('total_tokens', 0):,d}" + \
                            f"\n  Completion: {data.get('completion_tokens', 0):,d}" + \
                            f"\n  Prompt: {data.get('prompt_tokens', 0):,d}"
            
            if data.get('finish_reason'):
                record.msg += f"\nFinish Reason: {data['finish_reason']}"
            if data.get('timestamp'):
                record.msg += f"\nTimestamp: {data['timestamp']}"
            if data.get('note'):
                record.msg += f"\nNote: {data['note']}"
            record.msg += "\n" + "-"*80
                
        elif hasattr(record, 'openai_error'):
            data = record.openai_error
            record.msg = "\n" + "!"*80 + "\n" + \
                        f"OpenAI Error - ID: {data.get('id', 'N/A')}\n" + \
                        f"Error Type: {data.get('error_type', 'N/A')}\n" + \
                        f"Error Message: {data.get('error_message', 'N/A')}\n" + \
                        f"Timestamp: {data.get('timestamp', datetime.now().isoformat())}"
            if data.get('note'):
                record.msg += f"\nNote: {data['note']}"
            record.msg += "\n" + "!"*80
                
        return super().format(record)

def cleanup_logging(logger):
    """Clean up logging handlers."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

_file_logger = None
_console_logger = None

def setup_logging():
    """Set up logging configuration."""
    global _file_logger, _console_logger
    
    if _file_logger is not None and _console_logger is not None:
        return _file_logger, _console_logger
        
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Get current month and year for log file name
    current_date = datetime.now()
    log_file = f"logs/requests_{current_date.strftime('%Y%m')}.log"

    # Create file logger for OpenAI requests
    file_logger = logging.getLogger('ai_agent.file')
    file_logger.setLevel(logging.INFO)
    cleanup_logging(file_logger)
    
    # Create console logger for user interaction
    console_logger = logging.getLogger('ai_agent.console')
    console_logger.setLevel(logging.INFO)
    cleanup_logging(console_logger)

    # File handler for OpenAI logs
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = OpenAIFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    
    # Console handler for user interaction
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    console_logger.addHandler(console_handler)
    
    _file_logger = file_logger
    _console_logger = console_logger
    return file_logger, console_logger

def get_logger(logger_type='console'):
    """Get the configured logger instance."""
    file_logger, console_logger = setup_logging()
    return file_logger if logger_type == 'file' else console_logger 