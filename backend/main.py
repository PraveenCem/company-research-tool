import json
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from fastapi.responses import StreamingResponse
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Report
from schemas import (
    ReportResponse,
    ResearchRequest,
    ReportRename,
)
from services.research_agent import research_company


app = FastAPI(
    title="Company Research Tool"
)


# =====================================================
# DATABASE
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "ok"
    }


# =====================================================
# GET ALL REPORTS
# =====================================================

@app.get(
    "/api/reports",
    response_model=list[ReportResponse],
)
def get_reports(
    db: Session = Depends(get_db),
):

    reports = (
        db.query(Report)
        .order_by(
            Report.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": report.id,
            "company_name": report.company_name,
            "report_name": report.report_name,

            "overview": (
                json.loads(report.overview)
                if report.overview
                else None
            ),

            "key_people": (
                json.loads(report.key_people)
                if report.key_people
                else None
            ),

            "news": (
                json.loads(report.news)
                if report.news
                else None
            ),

            "financials": (
                json.loads(report.financials)
                if report.financials
                else None
            ),

            "risks": (
                json.loads(report.risks)
                if report.risks
                else None
            ),

            "created_at": report.created_at,
        }
        for report in reports
    ]


# =====================================================
# GET SINGLE REPORT
# =====================================================

@app.get(
    "/api/reports/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return {
        "id": report.id,

        "company_name":
            report.company_name,

        "report_name":
            report.report_name,

        "overview": (
            json.loads(
                report.overview
            )
            if report.overview
            else None
        ),

        "key_people": (
            json.loads(
                report.key_people
            )
            if report.key_people
            else None
        ),

        "news": (
            json.loads(
                report.news
            )
            if report.news
            else None
        ),

        "financials": (
            json.loads(
                report.financials
            )
            if report.financials
            else None
        ),

        "risks": (
            json.loads(
                report.risks
            )
            if report.risks
            else None
        ),

        "created_at":
            report.created_at,
    }


# =====================================================
# RESEARCH COMPANY
# =====================================================

@app.post("/api/research")
async def research(
    request: ResearchRequest,
    db: Session = Depends(get_db),
):

    async def event_stream():

        report_data = {}

        # ---------------------------------------------
        # Run research agent
        # ---------------------------------------------

        async for event in research_company(
            request.company_name
        ):

            section = event["section"]

            report_data[
                section
            ] = event["data"]

            # Send SSE event to React
            yield (
                f"data: "
                f"{json.dumps(event)}"
                f"\n\n"
            )

        # ---------------------------------------------
        # Save completed report
        # ---------------------------------------------

        report = Report(

            company_name=
                request.company_name,

            # Initial report name
            # defaults to company name
            report_name=
                request.company_name,

            overview=json.dumps(
                report_data.get(
                    "overview"
                )
            ),

            key_people=json.dumps(
                report_data.get(
                    "key_people"
                )
            ),

            news=json.dumps(
                report_data.get(
                    "news"
                )
            ),

            financials=json.dumps(
                report_data.get(
                    "financials"
                )
            ),

            risks=json.dumps(
                report_data.get(
                    "risks"
                )
            ),
        )

        db.add(report)

        db.commit()

        db.refresh(report)

        # ---------------------------------------------
        # Tell React research is complete
        # ---------------------------------------------

        complete_event = {
            "type": "complete",
            "report_id": report.id,
        }

        yield (
            f"data: "
            f"{json.dumps(complete_event)}"
            f"\n\n"
        )

    # ---------------------------------------------
    # SSE response
    # ---------------------------------------------

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# =====================================================
# DELETE REPORT
# =====================================================

@app.delete(
    "/api/reports/{report_id}"
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    db.delete(report)

    db.commit()

    return {
        "message":
            "Report deleted successfully"
    }


# =====================================================
# RENAME REPORT
# =====================================================

@app.put(
    "/api/reports/{report_id}"
)
def rename_report(
    report_id: int,
    request: ReportRename,
    db: Session = Depends(get_db),
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    report_name = (
        request.report_name.strip()
    )

    if not report_name:
        raise HTTPException(
            status_code=400,
            detail="Report name cannot be empty",
        )

    # ---------------------------------------------
    # Update report name
    # ---------------------------------------------

    report.report_name = report_name

    db.commit()

    db.refresh(report)

    return {
        "message":
            "Report renamed successfully",

        "report_name":
            report.report_name,
    }

# =====================================================
# DOWNLOAD REPORT AS PDF
# =====================================================

@app.get("/api/reports/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    # ---------------------------------------------
    # Parse stored JSON
    # ---------------------------------------------

    overview = (
        json.loads(report.overview)
        if report.overview
        else None
    )

    key_people = (
        json.loads(report.key_people)
        if report.key_people
        else []
    )

    news = (
        json.loads(report.news)
        if report.news
        else []
    )

    financials = (
        json.loads(report.financials)
        if report.financials
        else {}
    )

    risks = (
        json.loads(report.risks)
        if report.risks
        else []
    )

    # ---------------------------------------------
    # Create PDF in memory
    # ---------------------------------------------

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    # ---------------------------------------------
    # Title
    # ---------------------------------------------

    report_title = (
        report.report_name
        or report.company_name
    )

    story.append(
        Paragraph(
            report_title,
            title_style,
        )
    )

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            f"<b>Company:</b> "
            f"{report.company_name}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Created:</b> "
            f"{report.created_at.strftime('%d %B %Y')}",
            body_style,
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # ---------------------------------------------
    # Overview
    # ---------------------------------------------

    story.append(
        Paragraph(
            "OVERVIEW",
            heading_style,
        )
    )

    if overview:

        overview_text = (
            overview.get("snippet")
            or "No overview available."
        )

        story.append(
            Paragraph(
                overview_text,
                body_style,
            )
        )

    else:

        story.append(
            Paragraph(
                "No overview available.",
                body_style,
            )
        )

    story.append(
        Spacer(1, 18)
    )

    # ---------------------------------------------
    # Key People
    # ---------------------------------------------

    story.append(
        Paragraph(
            "KEY PEOPLE",
            heading_style,
        )
    )

    if key_people:

        people_data = [
            ["Name", "Title", "Source"]
        ]

        for person in key_people:

            people_data.append(
                [
                    person.get(
                        "name",
                        "N/A",
                    ),
                    person.get(
                        "title",
                        "N/A",
                    ),
                    person.get(
                        "source",
                        "N/A",
                    ),
                ]
            )

        table = Table(
            people_data,
            repeatRows=1,
            colWidths=[
                180,
                100,
                120,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(table)

    else:

        story.append(
            Paragraph(
                "No key people found.",
                body_style,
            )
        )

    story.append(
        Spacer(1, 18)
    )

    # ---------------------------------------------
    # News
    # ---------------------------------------------

    story.append(
        Paragraph(
            "RECENT NEWS",
            heading_style,
        )
    )

    if news:

        for item in news:

            title = item.get(
                "title",
                "Untitled",
            )

            snippet = item.get(
                "snippet",
                "",
            )

            source = item.get(
                "source",
                "",
            )

            story.append(
                Paragraph(
                    f"<b>{title}</b>",
                    body_style,
                )
            )

            if snippet:

                story.append(
                    Paragraph(
                        snippet,
                        body_style,
                    )
                )

            if source:

                story.append(
                    Paragraph(
                        f"<i>Source: {source}</i>",
                        body_style,
                    )
                )

            story.append(
                Spacer(1, 8)
            )

    else:

        story.append(
            Paragraph(
                "No news found.",
                body_style,
            )
        )

    story.append(
        Spacer(1, 10)
    )

    # ---------------------------------------------
    # Financial Highlights
    # ---------------------------------------------

    story.append(
        Paragraph(
            "FINANCIAL HIGHLIGHTS",
            heading_style,
        )
    )

    financial_data = [
        [
            "Metric",
            "Value",
        ],
        [
            "Revenue",
            financials.get(
                "revenue"
            ) or "N/A",
        ],
        [
            "Employees",
            str(
                financials.get(
                    "employee_count"
                )
                or "N/A"
            ),
        ],
        [
            "Market Cap",
            financials.get(
                "market_cap"
            ) or "N/A",
        ],
        [
            "YoY Growth",
            financials.get(
                "yoy_growth"
            ) or "N/A",
        ],
    ]

    financial_table = Table(
        financial_data,
        colWidths=[
            180,
            220,
        ],
    )

    financial_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        financial_table
    )

    story.append(
        Spacer(1, 18)
    )

    # ---------------------------------------------
    # Risks
    # ---------------------------------------------

    story.append(
        Paragraph(
            "RISKS",
            heading_style,
        )
    )

    if risks:

        for item in risks:

            title = item.get(
                "title",
                "Risk",
            )

            snippet = item.get(
                "snippet",
                "",
            )

            source = item.get(
                "source",
                "",
            )

            story.append(
                Paragraph(
                    f"<b>{title}</b>",
                    body_style,
                )
            )

            if snippet:

                story.append(
                    Paragraph(
                        snippet,
                        body_style,
                    )
                )

            if source:

                story.append(
                    Paragraph(
                        f"<i>Source: {source}</i>",
                        body_style,
                    )
                )

            story.append(
                Spacer(1, 8)
            )

    else:

        story.append(
            Paragraph(
                "No risks found.",
                body_style,
            )
        )

    # ---------------------------------------------
    # Build PDF
    # ---------------------------------------------

    document.build(story)

    buffer.seek(0)

    filename = (
        f"{report_title}"
        .replace(" ", "_")
        .replace("/", "_")
        + ".pdf"
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )
# Date: 2026-10-26