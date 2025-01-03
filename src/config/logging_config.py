"""Logging configuration for the application."""
import logging
import os
import traceback
from datetime import datetime
import json

class CustomFormatter(logging.Formatter):
    """Custom formatter that properly handles extra fields."""
    
    def format(self, record):
        """Format the record with extra fields."""
        # Format the basic message
        formatted = super().format(record)
        
        # Add extra fields if they exist
        if hasattr(record, 'extra'):
            extra_formatted = json.dumps(record.extra, indent=2)
            formatted += f"\nExtra Data:\n{extra_formatted}"
            
        return formatted

def setup_logging():
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Get the current month and year for the log file name
    current_date = datetime.now()
    log_file = f'logs/requests_{current_date.strftime("%Y%m")}.log'

    # Create logger
    logger = logging.getLogger('ai_agent')
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Set file handler to DEBUG level

    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatters
    file_formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

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