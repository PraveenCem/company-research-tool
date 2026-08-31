export interface SourceItem {
  title: string;
  snippet: string | null;
  source: string | null;
  url: string | null;
}

export interface FinancialHighlights {
  revenue: string | null;
  employee_count: number | null;
  market_cap: string | null;
  yoy_growth: string | null;

  revenue_source?: string | null;
  revenue_url?: string | null;

  sources?: SourceItem[];
}

export interface Overview {
  company: string;
  title: string | null;
  snippet: string | null;
  source: string | null;
  url: string | null;
}

export interface Report {
  id: number;
  company_name: string;

  overview: Overview | null;

  key_people: KeyPerson[] | null;

  news: SourceItem[] | null;

  financials: FinancialHighlights | null;

  risks: SourceItem[] | null;

  created_at: string;
}

export interface ResearchRequest {
  company_name: string;
}

export interface ResearchSectionEvent {
  type: "section";

  section:
    | "overview"
    | "key_people"
    | "news"
    | "financials"
    | "risks";

  data:
    | Overview
    | SourceItem[]
    | FinancialHighlights;
}

export interface ResearchCompleteEvent {
  type: "complete";
  report_id: number;
}

export type ResearchEvent =
  | ResearchSectionEvent
  | ResearchCompleteEvent;

export interface KeyPerson {
  name: string;
  title: string;
  source: string | null;
  url: string | null;
}