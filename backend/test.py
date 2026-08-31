import asyncio

from services.llm_service import generate_report


async def main():
    search_results = [
        {
            "title": "Microsoft company information",
            "link": "https://example.com",
            "snippet": (
                "Microsoft is a technology company "
                "that develops software, cloud services "
                "and other products."
            ),
        }
    ]

    report = await generate_report(
        "Microsoft",
        search_results,
    )

    print(report)


asyncio.run(main())