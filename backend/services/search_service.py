import os

from dotenv import load_dotenv
from tavily import AsyncTavilyClient

load_dotenv()

USE_MOCK_SERVICES = (
    os.getenv("USE_MOCK_SERVICES", "false").lower()
    == "true"
)


def mock_search(query: str) -> list[dict]:
    return [
        {
            "title": "Mock Company Overview",
            "link": "https://example.com/company",
            "snippet": (
                "This is mock company information."
            ),
        },
        {
            "title": "Mock Company Leadership",
            "link": "https://example.com/leadership",
            "snippet": (
                "This is mock leadership information."
            ),
        },
        {
            "title": "Mock Company News",
            "link": "https://example.com/news",
            "snippet": (
                "This is mock company news."
            ),
        },
    ]


async def search_web(
    query: str,
    num_results: int = 5,
) -> list[dict]:

    if USE_MOCK_SERVICES:
        return mock_search(query)

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing."
        )

    client = AsyncTavilyClient(
        api_key=api_key
    )

    response = await client.search(
        query=query,
        search_depth="basic",
        max_results=num_results,
    )

    return [
        {
            "title": result.get("title"),
            "link": result.get("url"),
            "snippet": result.get("content"),
        }
        for result in response.get(
            "results",
            []
        )
    ]