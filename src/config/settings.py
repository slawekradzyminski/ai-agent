import os
import logging
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').strip()
if LOG_LEVEL not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
    LOG_LEVEL = 'INFO'

AGENT_MODEL = "gpt-3.5-turbo"
AGENT_TEMPERATURE = 0.7
AGENT_MAX_ITERATIONS = 5
