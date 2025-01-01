"""Configuration settings for the AI agent."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').strip()
if LOG_LEVEL not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
    LOG_LEVEL = 'INFO'

# Agent Configuration
AGENT_MODEL = "gpt-3.5-turbo"  # Default model
AGENT_TEMPERATURE = 0.7  # Default temperature for model responses
AGENT_MAX_ITERATIONS = 5  # Maximum number of iterations for agent tasks 