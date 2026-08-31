import asyncio

from services.search_service import search_web


async def main():

    results = await search_web(
        "Apple recent news",
        num_results=5,
    )

    print("\nRESULT COUNT:")
    print(len(results))

    print("\nRESULTS:")

    for result in results:
        print("\nTITLE:")
        print(result["title"])

        print("\nLINK:")
        print(result["link"])

        print("\nSNIPPET:")
        print(result["snippet"])

        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())