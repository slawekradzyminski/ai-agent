"""Setup file for the AI agent package."""
from setuptools import setup, find_packages

setup(
    name="ai-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain==0.3.13",
        "langchain-community==0.3.13",
        "langchain-core==0.3.28",
        "langchain-openai==0.0.8",
        "python-dotenv==1.0.1",
        "openai==1.58.1",
        "duckduckgo-search==7.1.1",
        "typing-extensions==4.9.0",
        "pydantic==2.6.3",
        "requests==2.32.3",
        "anyio==4.7.0",
        "httpx==0.28.1",
        "aiohttp==3.11.11",
        "tenacity==9.0.0"
    ],
    python_requires=">=3.9",
) 