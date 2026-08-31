import asyncio
import os

from dotenv import load_dotenv
from tavily import AsyncTavilyClient

load_dotenv()


async def main():
    api_key = os.getenv("TAVILY_API_KEY")

    print("Tavily API key loaded:", bool(api_key))

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing"
        )

    client = AsyncTavilyClient(
        api_key=api_key
    )

    response = await client.search(
        query="Microsoft recent news",
        search_depth="basic",
        max_results=5,
    )

    print("\nSearch results:\n")

    for result in response["results"]:
        print("TITLE:", result.get("title"))
        print("URL:", result.get("url"))
        print("CONTENT:", result.get("content"))
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())