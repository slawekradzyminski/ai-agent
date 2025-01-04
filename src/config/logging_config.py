"""Logging configuration for the application."""
import os
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

class OpenAIFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'openai_request'):
            data = record.openai_request
            record.msg = f"OpenAI Request - ID: {data.get('id', 'N/A')}\n" + \
                        f"Model: {data.get('model', 'N/A')}\n" + \
                        f"Temperature: {data.get('temperature', 'N/A')}\n" + \
                        f"Messages: {json.dumps(data.get('messages', []), indent=2)}"
            if 'timestamp' in data:
                record.msg += f"\nTimestamp: {data['timestamp']}"
        elif hasattr(record, 'openai_response'):
            data = record.openai_response
            record.msg = f"OpenAI Response - ID: {data.get('id', 'N/A')}\n" + \
                        f"Model: {data.get('model', 'N/A')}\n" + \
                        f"Content: {data.get('content', 'N/A')}\n" + \
                        f"Tokens - Total: {data.get('total_tokens', 'N/A')}, " + \
                        f"Completion: {data.get('completion_tokens', 'N/A')}, " + \
                        f"Prompt: {data.get('prompt_tokens', 'N/A')}"
            if 'finish_reason' in data:
                record.msg += f"\nFinish Reason: {data['finish_reason']}"
            if 'timestamp' in data:
                record.msg += f"\nTimestamp: {data['timestamp']}"
        elif hasattr(record, 'openai_error'):
            data = record.openai_error
            record.msg = f"OpenAI Error - ID: {data.get('id', 'N/A')}\n" + \
                        f"Error Type: {data.get('error_type', 'N/A')}\n" + \
                        f"Error Message: {data.get('error_message', 'N/A')}"
            if 'timestamp' in data:
                record.msg += f"\nTimestamp: {data['timestamp']}"
        return super().format(record)

def cleanup_logging(logger):
    """Clean up logging handlers."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

def setup_logging() -> logging.Logger:
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Get current month and year for log file name
    current_date = datetime.now()
    log_file = f"logs/requests_{current_date.strftime('%Y%m')}.log"

    # Create logger
    logger = logging.getLogger('ai_agent')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatters
    file_formatter = OpenAIFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

request_logger = setup_logging() 