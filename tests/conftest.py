import pytest
import logging
import tempfile
import os
from src.config.logging_config import cleanup_logging, get_logger
from src.config.formatters import OpenAIFormatter

@pytest.fixture(autouse=True)
def temp_log_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_file = os.path.join(temp_dir, "test.log")
        original_log_file = os.environ.get("LOG_FILE_PATH")
        os.environ["LOG_FILE_PATH"] = temp_log_file
        yield temp_log_file
        if original_log_file:
            os.environ["LOG_FILE_PATH"] = original_log_file
        else:
            del os.environ["LOG_FILE_PATH"]

@pytest.fixture(autouse=True)
def cleanup_logs():
    global _file_logger, _console_logger
    from src.config.logging_config import _file_logger, _console_logger
    _file_logger = None
    _console_logger = None
    
    for name in ['ai_agent', 'ai_agent.file', 'ai_agent.console']:
        logger = logging.getLogger(name)
        cleanup_logging(logger)
        
    yield

@pytest.fixture(autouse=True)
def caplog_with_formatter(caplog):
    handler = caplog.handler
    handler.setFormatter(OpenAIFormatter('%(message)s'))
    return caplog 