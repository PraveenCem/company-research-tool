import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Report
from schemas import ReportResponse, ResearchRequest
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

            "company_name":
                report.company_name,

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

@app.delete("/api/reports/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .filter(Report.id == report_id)
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
        "message": "Report deleted successfully"
    }