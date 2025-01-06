"""Logging configuration for the application."""
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from src.config.formatters import OpenAIFormatter

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
        
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file = os.environ.get("LOG_FILE_PATH")
    if not log_file:
        current_date = datetime.now()
        log_file = f"logs/requests_{current_date.strftime('%Y%m')}.log"

    file_logger = logging.getLogger('ai_agent.file')
    file_logger.setLevel(logging.INFO)
    cleanup_logging(file_logger)
    
    console_logger = logging.getLogger('ai_agent.console')
    console_logger.setLevel(logging.INFO)
    cleanup_logging(console_logger)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024, # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = OpenAIFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    
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