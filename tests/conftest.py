"""Shared test fixtures."""
import pytest
import logging
from src.config.logging_config import cleanup_logging

@pytest.fixture(autouse=True)
def cleanup_logs():
    """Clean up logging handlers after each test."""
    yield
    logger = logging.getLogger('ai_agent')
    cleanup_logging(logger) 