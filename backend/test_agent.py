import asyncio

from services.research_agent import research_company


async def main():
    async for event in research_company("Microsoft"):
        print(event)


asyncio.run(main())
# Date: 2026-10-26