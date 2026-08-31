import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

USE_MOCK_SERVICES = (
    os.getenv("USE_MOCK_SERVICES", "false").lower()
    == "true"
)

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def mock_report(company_name: str) -> dict:
    return {
        "overview": (
            f"{company_name} is a technology company "
            "providing products, services, and business "
            "solutions to customers."
        ),
        "key_people": [
            {
                "name": f"{company_name} Executive",
                "title": "Chief Executive Officer",
            }
        ],
        "news": [
            f"{company_name} announced recent product "
            "and business developments.",
            f"{company_name} continues strategic "
            "partnerships and initiatives.",
            f"{company_name} reported recent "
            "operational developments.",
        ],
        "financials": {
            "revenue": None,
            "employee_count": None,
            "market_cap": None,
            "yoy_growth": None,
        },
        "risks": [
            f"Competitive pressure affecting "
            f"{company_name}.",
            f"Regulatory and compliance risks "
            f"affecting {company_name}.",
        ],
    }


async def generate_report(
    company_name: str,
    search_results: list[dict],
) -> dict:

    # ---------------------------------
    # MOCK MODE
    # ---------------------------------

    if USE_MOCK_SERVICES:
        return mock_report(company_name)

    # ---------------------------------
    # REAL OPENAI MODE
    # ---------------------------------

    research_data = json.dumps(
        search_results,
        indent=2,
    )

    prompt = f"""
You are a company research analyst helping a
sales representative prepare for a meeting.

Research company: {company_name}

Use ONLY the information provided in the
web search results below.

Do not invent facts or numbers.

WEB SEARCH RESULTS:
{research_data}

Create a structured company briefing with
exactly these five sections.

1. Company Overview

Explain:

- What the company does
- Industry
- Core products/services
- Target customers
- Market positioning

2. Key People

Include relevant senior executives.

Examples:

- CEO
- CTO
- CFO
- CIO
- CISO

Return an array of objects with:

name
title

3. Recent News

Return 3-4 important recent developments.

Focus on:

- acquisitions
- earnings
- product launches
- partnerships
- layoffs
- leadership changes

Use current information from the
search results.

4. Financial Highlights

Return:

- revenue
- employee_count
- market_cap
- yoy_growth

If a metric is unavailable,
return null.

Never fabricate financial numbers.

5. Risk Factors

Return 2-3 relevant risks.

Examples:

- regulatory scrutiny
- security issues
- competitive threats
- litigation
- financial instability

Return ONLY valid JSON in this structure:

{{
    "overview": "string",

    "key_people": [
        {{
            "name": "string",
            "title": "string"
        }}
    ],

    "news": [
        "string"
    ],

    "financials": {{
        "revenue": "string or null",
        "employee_count": "integer or null",
        "market_cap": "string or null",
        "yoy_growth": "string or null"
    }},

    "risks": [
        "string"
    ]
}}
"""

    response = await client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    return json.loads(
        response.output_text
    )