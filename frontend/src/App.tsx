import { useEffect, useState } from "react";
import "./App.css";

import {
  getReport,
  getReports,
  deleteReport,
  researchCompany,
} from "./api";

import type {
  FinancialHighlights,
  KeyPerson,
  Overview,
  Report,
  ResearchEvent,
  SourceItem,
} from "./types";

const sections = [
  "overview",
  "key_people",
  "news",
  "financials",
  "risks",
] as const;

type SectionName = (typeof sections)[number];

const sectionLabels: Record<SectionName, string> = {
  overview: "Company Overview",
  key_people: "Key People",
  news: "Recent News",
  financials: "Financial Highlights",
  risks: "Risk Factors",
};

function SourceLink({
  url,
}: {
  url: string | null | undefined;
}) {
  if (!url) {
    return null;
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="source-link"
    >
      View Source ↗
    </a>
  );
}

function App() {
  const [companyName, setCompanyName] = useState("");

  const [reports, setReports] = useState<Report[]>([]);
  const [historyLoading, setHistoryLoading] =
    useState(true);

  const [isResearching, setIsResearching] =
    useState(false);

  const [error, setError] = useState("");

  const [overview, setOverview] =
    useState<Overview | null>(null);

  const [keyPeople, setKeyPeople] =
    useState<KeyPerson[]>([]);

  const [news, setNews] =
    useState<SourceItem[]>([]);

  const [financials, setFinancials] =
    useState<FinancialHighlights | null>(null);

  const [risks, setRisks] =
    useState<SourceItem[]>([]);

  const [reportId, setReportId] =
    useState<number | null>(null);

  const [completedSections, setCompletedSections] =
    useState<SectionName[]>([]);

  const [currentSection, setCurrentSection] =
    useState<SectionName | null>(null);

  // ===================================================
  // LOAD HISTORY
  // ===================================================

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await getReports();

        setReports(data);
      } catch (error) {
        console.error(
          "Failed to load history:",
          error
        );
      } finally {
        setHistoryLoading(false);
      }
    };

    loadHistory();
  }, []);

  // ===================================================
  // CLEAR REPORT
  // ===================================================

  const clearReport = () => {
    setOverview(null);
    setKeyPeople([]);
    setNews([]);
    setFinancials(null);
    setRisks([]);
    setCompanyName("");


    setReportId(null);
    setCompletedSections([]);
    setCurrentSection(null);
  };

  const handleDeleteReport = async (
    id: number
  ) => {
    if (isResearching) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete this report?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteReport(id);

      setReports((previous) =>
        previous.filter(
          (report) => report.id !== id
        )
      );

      if (reportId === id) {
        clearReport();
      }
    } catch (error) {
      console.error(
        "Failed to delete report:",
        error
      );

      setError(
        "Failed to delete the report."
      );
    }
  };

  // ===================================================
  // START RESEARCH
  // ===================================================

  const handleResearch = async () => {
    const name = companyName.trim();

    if (isResearching) {
      return;
    }

    if (!name) {
      setError("Please enter a company name.");
      setCompanyName("");
        setTimeout(()=>{
          setError("");
        },1000);
          
      return;
    }

    setIsResearching(true);
    setError("");

    clearReport();

    try {
      await researchCompany(
        name,
        (event: ResearchEvent) => {
          console.log(
            "SSE event:",
            event
          );

          // -------------------------------------------
          // SECTION EVENT
          // -------------------------------------------

          if (event.type === "section") {
            setCurrentSection(
              event.section
            );

            setCompletedSections(
              (previous) => {
                if (
                  previous.includes(
                    event.section
                  )
                ) {
                  return previous;
                }

                return [
                  ...previous,
                  event.section,
                ];
              }
            );

            switch (event.section) {
              case "overview":
                setOverview(
                  event.data as Overview
                );
                break;

              case "key_people":
                setKeyPeople(
                  event.data as KeyPerson[]
                );
                break;

              case "news":
                setNews(
                  event.data as SourceItem[]
                );
                break;

              case "financials":
                setFinancials(
                  event.data as FinancialHighlights
                );
                break;

              case "risks":
                setRisks(
                  event.data as SourceItem[]
                );
                break;
            }
          }

          // -------------------------------------------
          // COMPLETE EVENT
          // -------------------------------------------

          if (event.type === "complete") {
            setReportId(
              event.report_id
            );

            setCurrentSection(null);
          }
        }
      );

      // ---------------------------------------------
      // REFRESH HISTORY
      // ---------------------------------------------

      const updatedReports =
        await getReports();

      setReports(updatedReports);
    } catch (error) {
      console.error(
        "Research failed:",
        error
      );

      setError(
        "Research failed. Please check the backend and try again."
      );
    } finally {
      setIsResearching(false);
    }
  };

  // ===================================================
  // LOAD EXISTING REPORT
  // ===================================================

  const handleSelectReport = async (
    id: number
  ) => {
    if (isResearching) {
      return;
    }

    try {
      setError("");

      const report =
        await getReport(id);

      setCompanyName(
        report.company_name
      );

      setOverview(
        report.overview ?? null
      );

      setKeyPeople(
        report.key_people ?? []
      );

      setNews(
        report.news ?? []
      );

      setFinancials(
        report.financials ?? null
      );

      setRisks(
        report.risks ?? []
      );

      setReportId(
        report.id
      );

      // ---------------------------------------------
      // MARK AVAILABLE SECTIONS
      // ---------------------------------------------

      const completed: SectionName[] =
        [];

      if (report.overview) {
        completed.push(
          "overview"
        );
      }

      if (
        report.key_people &&
        report.key_people.length > 0
      ) {
        completed.push(
          "key_people"
        );
      }

      if (
        report.news &&
        report.news.length > 0
      ) {
        completed.push(
          "news"
        );
      }

      if (report.financials) {
        completed.push(
          "financials"
        );
      }

      if (
        report.risks &&
        report.risks.length > 0
      ) {
        completed.push(
          "risks"
        );
      }

      setCompletedSections(
        completed
      );

      setCurrentSection(null);
    } catch (error) {
      console.error(
        "Failed to load report:",
        error
      );

      setError(
        "Failed to load the selected report."
      );
    }
  };

  // ===================================================
  // UI
  // ===================================================

  return (
    <div className="app">

      {/* =================================================
          HEADER
      ================================================= */}

      <header className="header">
        <div>
          <h1>
            Company Research Tool
          </h1>

          <p>
            Research a company and get
            a source-backed briefing.
          </p>
        </div>
      </header>

      <div className="layout">

        {/* =================================================
            HISTORY
        ================================================= */}

        <aside className="history">

          <div className="history-header">
            <h2>
              Research History
            </h2>
          </div>

          {historyLoading && (
            <p className="history-empty">
              Loading...
            </p>
          )}

          {!historyLoading &&
            reports.length === 0 && (
              <p className="history-empty">
                No previous reports.
              </p>
            )}

          <div className="history-list">
            {reports.map((report) => (
              <button
                key={report.id}
                className={`history-item ${reportId === report.id ? "active" : ""
                  }`}
                onClick={() =>
                  handleSelectReport(report.id)
                }
              >
                <strong>
                  {report.company_name}
                </strong>

                <span>
                  {new Date(
                    report.created_at
                  ).toLocaleDateString()}
                </span>
              </button>
            ))}

          </div>

        </aside>

        {/* =================================================
            MAIN
        ================================================= */}

        <main className="main">

          {/* =================================================
              SEARCH
          ================================================= */}

          
          {error && (
            <p className="error">
              {error}
            </p>
          )}
          <p></p>

          <div className="search-box">

            <input
              type="text"
              value={companyName}
              onChange={(event) =>
                setCompanyName(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleResearch();
                }
              }}
              placeholder="Enter company name..."
              disabled={isResearching}
            />

            {reportId === null && (
              <button
                type="button"
                onClick={handleResearch}
                disabled={isResearching}
              >
                {isResearching
                  ? "Researching..."
                  : "Research"}
              </button>
            )}

          </div>

          {/* =================================================
              ERROR
          ================================================= */}


          {/* =================================================
              PROGRESS
          ================================================= */}

          {isResearching && (
            <div className="research-status">

              <div className="research-heading">

                <div className="spinner" />

                <div>
                  <strong>
                    Researching{" "}
                    {companyName}...
                  </strong>

                  <span>
                    Gathering information
                    from multiple sources.
                  </span>
                </div>

              </div>

              <div className="progress-list">

                {sections.map(
                  (section) => {
                    const completed =
                      completedSections.includes(
                        section
                      );

                    const current =
                      currentSection ===
                      section;

                    return (
                      <div
                        key={section}
                        className={`progress-item ${completed
                          ? "completed"
                          : ""
                          } ${current
                            ? "current"
                            : ""
                          }`}
                      >

                        <span className="progress-icon">
                          {completed
                            ? "✓"
                            : current
                              ? "⟳"
                              : "○"}
                        </span>

                        <span>
                          {
                            sectionLabels[
                            section
                            ]
                          }
                        </span>

                      </div>
                    );
                  }
                )}

              </div>

            </div>
          )}

          {/* =================================================
              REPORT ID
          ================================================= */}

          {reportId !== null && (
            <div className="report-header">

              <button
                type="button"
                className="back-button"
                onClick={clearReport}
              >
                ← Back to Research
              </button>

              <div className="report-header-info">
                <p className="report-id">
                  Report #{reportId}
                </p>

                <p className="report-date">
                  Research report
                </p>
              </div>

              <button
                type="button"
                className="delete-report-button"
                onClick={() =>
                  handleDeleteReport(reportId)
                }
                disabled={isResearching}
              >
                Delete Report
              </button>

            </div>
          )}

          {/* =================================================
              OVERVIEW
          ================================================= */}

          {overview && (
            <section className="report-section">

              <div className="section-heading">

                <div>
                  <p className="section-eyebrow">
                    OVERVIEW
                  </p>

                  <h2>
                    {overview.company}
                  </h2>
                </div>

              </div>

              {overview.title && (
                <h3 className="overview-title">
                  {overview.title}
                </h3>
              )}

              <p className="overview-text">
                {overview.snippet}
              </p>

              <SourceLink
                url={overview.url}
              />

            </section>
          )}

          {/* =================================================
              KEY PEOPLE
          ================================================= */}

          {keyPeople.length > 0 && (
            <section className="report-section">

              <div className="section-heading">

                <div>
                  <p className="section-eyebrow">
                    LEADERSHIP
                  </p>

                  <h2>
                    Key People
                  </h2>
                </div>

              </div>

              <div className="source-grid">

                {keyPeople.map(
                  (person, index) => (
                    <article
                      className="source-card person-card"
                      key={`${person.name}-${person.title}-${index}`}
                    >

                      <div className="person-icon">
                        (person.name ?? "?").charAt(0)
                      </div>

                      <div className="source-card-content">

                        <h3>
                          {person.name}
                        </h3>

                        <p>
                          {person.title}
                        </p>

                        <div className="source-meta">

                          <span>
                            {person.source}
                          </span>

                          <SourceLink
                            url={person.url}
                          />

                        </div>

                      </div>

                    </article>
                  )
                )}

              </div>

            </section>
          )}

          {/* =================================================
              NEWS
          ================================================= */}

          {news.length > 0 && (
            <section className="report-section">

              <div className="section-heading">

                <div>
                  <p className="section-eyebrow">
                    LATEST
                  </p>

                  <h2>
                    Recent News
                  </h2>
                </div>

              </div>

              <div className="source-list">

                {news.map(
                  (item, index) => (
                    <article
                      className="source-card"
                      key={`${item.title}-${index}`}
                    >

                      <h3>
                        {item.title}
                      </h3>

                      {item.snippet && (
                        <p>
                          {item.snippet}
                        </p>
                      )}

                      <div className="source-meta">

                        <span>
                          {item.source}
                        </span>

                        <SourceLink
                          url={item.url}
                        />

                      </div>

                    </article>
                  )
                )}

              </div>

            </section>
          )}

          {/* =================================================
              FINANCIALS
          ================================================= */}

          {financials && (
            <section className="report-section">

              <div className="section-heading">

                <div>
                  <p className="section-eyebrow">
                    NUMBERS
                  </p>

                  <h2>
                    Financial Highlights
                  </h2>
                </div>

              </div>

              <div className="financial-grid">

                <div className="financial-card">
                  <span>
                    Revenue
                  </span>

                  <strong>
                    {financials.revenue ??
                      "N/A"}
                  </strong>
                </div>

                <div className="financial-card">
                  <span>
                    Employees
                  </span>

                  <strong>
                    {financials.employee_count
                      ?.toLocaleString() ??
                      "N/A"}
                  </strong>
                </div>

                <div className="financial-card">
                  <span>
                    Market Cap
                  </span>

                  <strong>
                    {financials.market_cap ??
                      "N/A"}
                  </strong>
                </div>

                <div className="financial-card">
                  <span>
                    YoY Growth
                  </span>

                  <strong>
                    {financials.yoy_growth ??
                      "N/A"}
                  </strong>
                </div>

              </div>

              {/* FINANCIAL SOURCES */}

              {financials.sources &&
                financials.sources.length >
                0 && (

                  <div className="financial-sources">

                    <h3>
                      Financial Sources
                    </h3>

                    {financials.sources.map(
                      (source, index) => (
                        <article
                          className="source-card"
                          key={`${source.title}-${index}`}
                        >

                          <h3>
                            {source.title}
                          </h3>

                          {source.snippet && (
                            <p>
                              {
                                source.snippet
                              }
                            </p>
                          )}

                          <div className="source-meta">

                            <span>
                              {
                                source.source
                              }
                            </span>

                            <SourceLink
                              url={
                                source.url
                              }
                            />

                          </div>

                        </article>
                      )
                    )}

                  </div>
                )}

            </section>
          )}

          {/* =================================================
              RISKS
          ================================================= */}

          {risks.length > 0 && (
            <section className="report-section">

              <div className="section-heading">

                <div>
                  <p className="section-eyebrow">
                    WATCH
                  </p>

                  <h2>
                    Risk Factors
                  </h2>
                </div>

              </div>

              <div className="source-list">

                {risks.map(
                  (risk, index) => (
                    <article
                      className="source-card risk-card"
                      key={`${risk.title}-${index}`}
                    >

                      <h3>
                        {risk.title}
                      </h3>

                      {risk.snippet && (
                        <p>
                          {risk.snippet}
                        </p>
                      )}

                      <div className="source-meta">

                        <span>
                          {risk.source}
                        </span>

                        <SourceLink
                          url={risk.url}
                        />

                      </div>

                    </article>
                  )
                )}

              </div>

            </section>
          )}

          {/* =================================================
              EMPTY STATE
          ================================================= */}

          {!isResearching &&
            !overview &&
            keyPeople.length === 0 &&
            news.length === 0 &&
            !financials &&
            risks.length === 0 && (

              <div className="empty-state">

                <div className="empty-icon">
                  ✦
                </div>

                <h2>
                  Start your research
                </h2>

                <p>
                  Enter a company name
                  above to generate a
                  source-backed research
                  briefing.
                </p>

              </div>
            )}

        </main>

      </div>

    </div>
  );
}

export default App;