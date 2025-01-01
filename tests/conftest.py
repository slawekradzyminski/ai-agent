"""Test configuration and fixtures."""
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from src.config.logging_config import setup_request_logger

@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up test-specific logging configuration."""
    # Create temporary directory for test logs
    temp_dir = tempfile.mkdtemp()
    log_dir = Path(temp_dir) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Store original log directory
    original_log_dir = os.environ.get("LOG_DIR")
    
    # Set test log directory
    os.environ["LOG_DIR"] = str(log_dir)
    
    # Reset logger to use test directory
    setup_request_logger()
    
    yield
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    # Restore original log directory
    if original_log_dir:
        os.environ["LOG_DIR"] = original_log_dir
    else:
        os.environ.pop("LOG_DIR", None)
    
    # Reset logger to use original directory
    setup_request_logger() 