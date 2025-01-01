"""Logging configuration for the application."""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

def setup_request_logger():
    """
    Set up a dedicated logger for external requests and responses.
    Uses rotating file handler to prevent log files from growing too large.
    """
    # Get log directory from environment or use default
    log_dir = Path(os.environ.get("LOG_DIR", "logs"))
    log_dir.mkdir(exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger("external_requests")
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Create rotating file handler (10MB per file, max 5 files)
    log_file = log_dir / f"requests_{datetime.now().strftime('%Y%m')}.log"
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Create formatter with clear separation between entries
    formatter = logging.Formatter(
        '\n%(asctime)s - %(name)s - %(levelname)s\n'
        '----------------------------------------\n'
        'REQUEST: %(request)s\n'
        'RESPONSE: %(response)s\n'
        '----------------------------------------\n'
    )
    
    # Set formatter for handler
    handler.setFormatter(formatter)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

# Create the logger instance
request_logger = setup_request_logger() 