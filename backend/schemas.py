from datetime import datetime

from pydantic import BaseModel


class SourceItem(BaseModel):
    title: str
    snippet: str | None = None
    source: str | None = None
    url: str | None = None


class FinancialHighlights(BaseModel):
    revenue: str | None = None
    employee_count: int | None = None
    market_cap: str | None = None
    yoy_growth: str | None = None

    sources: list[dict] | None = None


class ReportResponse(BaseModel):
    id: int
    company_name: str

    overview: dict | None = None

    key_people: list[SourceItem] | None = None

    news: list[SourceItem] | None = None

    financials: FinancialHighlights | None = None

    risks: list[SourceItem] | None = None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ResearchRequest(BaseModel):
    company_name: str