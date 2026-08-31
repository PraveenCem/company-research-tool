import asyncio
import re

from collections.abc import AsyncGenerator

from services.search_service import search_web


# =====================================================
# RESEARCH COMPANY
# =====================================================

async def research_company(
    company_name: str,
) -> AsyncGenerator[dict, None]:

    (
        overview_results,
        leadership_results,
        news_results,
        financial_results,
        risk_results,
    ) = await asyncio.gather(

        # ---------------------------------------------
        # Overview
        # ---------------------------------------------

        search_web(
            f"{company_name} company overview products services industry",
            num_results=5,
        ),

        # ---------------------------------------------
        # Leadership
        # ---------------------------------------------

        search_web(
            f"{company_name} official leadership executives CEO CFO CTO",
            num_results=5,
        ),

        # ---------------------------------------------
        # News
        # ---------------------------------------------

        search_web(
            f"{company_name} latest news August 2026",
            num_results=5,
        ),

        # ---------------------------------------------
        # Financials
        # ---------------------------------------------

        search_web(
            f"{company_name} latest annual report revenue employees "
            f"market capitalization year over year growth "
            f"investor relations financial results",
            num_results=10,
        ),

        # ---------------------------------------------
        # Risks
        # ---------------------------------------------

        search_web(
            f"{company_name} latest lawsuits regulatory risks "
            f"competition security",
            num_results=5,
        ),
    )

    # =================================================
    # DEBUG FINANCIAL RESULTS
    # =================================================

    print("\n========== FINANCIAL RESULTS ==========")

    for result in financial_results:

        print("\nTITLE:")
        print(result.get("title"))

        print("URL:")
        print(result.get("link"))

        print("SNIPPET:")
        print(result.get("snippet"))

    print("\n========================================\n")

    # =================================================
    # OVERVIEW
    # =================================================

    overview = build_overview(
        company_name,
        overview_results,
    )

    yield {
        "type": "section",
        "section": "overview",
        "data": overview,
    }

    # =================================================
    # KEY PEOPLE
    # =================================================

    key_people = build_key_people(
        leadership_results
    )

    yield {
        "type": "section",
        "section": "key_people",
        "data": key_people,
    }

    # =================================================
    # NEWS
    # =================================================

    news = build_source_results(
        news_results,
        limit=5,
    )

    yield {
        "type": "section",
        "section": "news",
        "data": news,
    }

    # =================================================
    # FINANCIALS
    # =================================================

    financials = build_financials(
        financial_results,
    )

    yield {
        "type": "section",
        "section": "financials",
        "data": financials,
    }

    # =================================================
    # RISKS
    # =================================================

    risks = build_source_results(
        risk_results,
        limit=5,
    )

    yield {
        "type": "section",
        "section": "risks",
        "data": risks,
    }


# =====================================================
# OVERVIEW
# =====================================================

def build_overview(
    company_name: str,
    results: list[dict],
) -> dict:

    if not results:
        return {
            "company": company_name,
            "title": None,
            "snippet": "No search results found.",
            "source": None,
            "url": None,
        }

    result = results[0]

    return {
        "company": company_name,
        "title": result.get("title"),
        "snippet": result.get("snippet"),
        "source": get_source_name(
            result.get("link")
        ),
        "url": result.get("link"),
    }


# =====================================================
# KEY PEOPLE
# =====================================================

def build_key_people(
    results: list[dict],
) -> list[dict]:

    people = []

    leadership_roles = {
        "ceo": "CEO",
        "chief executive officer": "CEO",
        "cfo": "CFO",
        "chief financial officer": "CFO",
        "cto": "CTO",
        "chief technology officer": "CTO",
        "coo": "COO",
        "chief operating officer": "COO",
        "president": "President",
        "chairman": "Chairman",
    }

    for result in results:

        title = result.get("title") or ""
        snippet = result.get("snippet") or ""
        url = result.get("link") or ""

        text = f"{title}\n{snippet}"

        for role_text, normalized_role in leadership_roles.items():

            if role_text.lower() not in text.lower():
                continue

            lines = text.splitlines()

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                lower_line = line.lower()

                if role_text.lower() not in lower_line:
                    continue

                # -------------------------------------
                # Name - Role
                # -------------------------------------

                if "-" in line:

                    name_part = line.split(
                        "-",
                        1,
                    )[0].strip()

                    if (
                        2 <= len(name_part.split()) <= 4
                    ):

                        person = {
                            "name": name_part,
                            "title": normalized_role,
                            "source": get_source_name(url),
                            "url": url,
                        }

                        if person not in people:
                            people.append(person)

                # -------------------------------------
                # Name (Role)
                # -------------------------------------

                if "(" in line:

                    name_part = line.split(
                        "(",
                        1,
                    )[0].strip()

                    if (
                        2 <= len(name_part.split()) <= 4
                    ):

                        person = {
                            "name": name_part,
                            "title": normalized_role,
                            "source": get_source_name(url),
                            "url": url,
                        }

                        if person not in people:
                            people.append(person)

                if len(people) >= 5:
                    return people

    return people


# =====================================================
# GENERIC SOURCE RESULTS
# =====================================================

def build_source_results(
    results: list[dict],
    limit: int = 5,
) -> list[dict]:

    output = []

    for result in results:

        title = (
            result.get("title") or ""
        ).strip()

        snippet = (
            result.get("snippet") or ""
        ).strip()

        url = result.get("link")

        if not title:
            continue

        item = {
            "title": title,
            "snippet": snippet,
            "source": get_source_name(url),
            "url": url,
        }

        if item not in output:
            output.append(item)

        if len(output) >= limit:
            break

    return output


# =====================================================
# FINANCIALS
# =====================================================

def build_financials(
    results: list[dict],
) -> dict:

    revenue = None
    employee_count = None
    market_cap = None
    yoy_growth = None

    revenue_source = None
    revenue_url = None

    for result in results:

        title = result.get("title") or ""
        snippet = result.get("snippet") or ""
        url = result.get("link") or ""

        text = f"{title} {snippet}"

        # =================================================
        # REVENUE
        # =================================================

        if revenue is None:

            revenue_patterns = [

                re.compile(
                    r"(?:revenue|revenues)"
                    r"(?:\s+was|\s+of|\s+reached|\s+totaled|\s*:)?"
                    r"\s*\$?\s*"
                    r"([\d,.]+)\s*"
                    r"(billion|million|trillion)",
                    re.IGNORECASE,
                ),

                re.compile(
                    r"(?:revenue|revenues)"
                    r".{0,40}?"
                    r"\$?\s*([\d,.]+)\s*"
                    r"(B|M|T)\b",
                    re.IGNORECASE,
                ),
            ]

            for pattern in revenue_patterns:

                match = pattern.search(text)

                if match:

                    amount = match.group(1)
                    unit = match.group(2)

                    unit_map = {
                        "b": "billion",
                        "m": "million",
                        "t": "trillion",
                    }

                    unit = unit_map.get(
                        unit.lower(),
                        unit.lower(),
                    )

                    revenue = (
                        f"${amount} {unit}"
                    )

                    revenue_source = (
                        get_source_name(url)
                    )

                    revenue_url = url

                    break

        # =================================================
        # EMPLOYEES
        # =================================================

        if employee_count is None:

            employee_patterns = [

                re.compile(
                    r"(?:employs|employees|workforce)"
                    r".{0,40}?"
                    r"([\d,]+)\s*"
                    r"(?:employees|people|workers)?",
                    re.IGNORECASE,
                ),

                re.compile(
                    r"([\d,]+)\s+employees",
                    re.IGNORECASE,
                ),
            ]

            for pattern in employee_patterns:

                match = pattern.search(text)

                if match:

                    value = (
                        match.group(1)
                        .replace(",", "")
                    )

                    try:
                        employee_count = int(value)
                    except ValueError:
                        employee_count = None

                    if employee_count:
                        break

        # =================================================
        # MARKET CAP
        # =================================================

        if market_cap is None:

            market_cap_patterns = [

                re.compile(
                    r"(?:market\s+cap|market\s+capitalization)"
                    r".{0,30}?"
                    r"\$?\s*([\d,.]+)\s*"
                    r"(billion|million|trillion|B|M|T)",
                    re.IGNORECASE,
                ),
            ]

            for pattern in market_cap_patterns:

                match = pattern.search(text)

                if match:

                    amount = match.group(1)
                    unit = match.group(2)

                    unit_map = {
                        "b": "billion",
                        "m": "million",
                        "t": "trillion",
                    }

                    unit = unit_map.get(
                        unit.lower(),
                        unit.lower(),
                    )

                    market_cap = (
                        f"${amount} {unit}"
                    )

                    break

        # =================================================
        # YOY GROWTH
        # =================================================

        if yoy_growth is None:

            growth_patterns = [

                re.compile(
                    r"(?:revenue|revenues)"
                    r".{0,80}?"
                    r"(?:increased|grew|growth|up)"
                    r".{0,20}?"
                    r"(\d+(?:\.\d+)?)\s*%",
                    re.IGNORECASE,
                ),

                re.compile(
                    r"(\d+(?:\.\d+)?)\s*%"
                    r".{0,20}?"
                    r"(?:year.over.year|yoy)",
                    re.IGNORECASE,
                ),
            ]

            for pattern in growth_patterns:

                match = pattern.search(text)

                if match:

                    yoy_growth = (
                        f"{match.group(1)}%"
                    )

                    break

    return {
        "revenue": revenue,
        "employee_count": employee_count,
        "market_cap": market_cap,
        "yoy_growth": yoy_growth,
        "revenue_source": revenue_source,
        "revenue_url": revenue_url,
        "sources": build_source_results(
            results,
            limit=5,
        ),
    }


# =====================================================
# SOURCE NAME
# =====================================================

def get_source_name(
    url: str | None,
) -> str | None:

    if not url:
        return None

    try:

        from urllib.parse import urlparse

        hostname = urlparse(url).hostname

        if not hostname:
            return None

        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except Exception:
        return None