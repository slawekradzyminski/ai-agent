import asyncio;from src.cli.handlers.browser import BrowserHandler;from src.agent.base import Agent;async def test():    handler = BrowserHandler(Agent());    content = await handler.handle("browser: https://www.awesome-testing.com/tips/deep-technical-understanding");    print("Content length:", len(content));    print("
Extracted content:
");    print(content);asyncio.run(test())
