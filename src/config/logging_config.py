"""Logging configuration for the application."""
import logging
import os
from datetime import datetime

def setup_logging():
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Get the current month and year for the log file name
    current_date = datetime.now()
    log_file = f'logs/requests_{current_date.strftime("%Y%m")}.log'

    # Create logger
    logger = logging.getLogger('ai_agent')
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        handler.close()  # Close the handler
        logger.removeHandler(handler)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def cleanup_logging(logger):
    """Clean up logging handlers."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

# Create the logger instance
request_logger = setup_logging() 