from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User, Product, ShopperSession
from app.services.scoring import calculate_attractiveness_score
from app.services.behavior import classify_shopper
from app.services.recommendations import generate_recommendations
from app.services.notifications import check_alerts
from app.services.export import export_excel, export_pdf

router = APIRouter(prefix="/api/reports", tags=["Reports"])

REPORTS_DIR = "app/static/reports"


def gather_report_data(db: Session):
    """Pulls real data from the DB and shapes it exactly like export.py expects."""

    # Scores
    products = db.query(Product).all()
    scores_data = []
    for p in products:
        score = calculate_attractiveness_score(
            attention_duration=p.attention_duration,
            interaction_frequency=p.interaction_frequency,
            pickup_rate=p.pickup_rate,
            conversion_rate=p.conversion_rate,
            repeat_engagement=p.repeat_engagement
        )
        rating = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"
        p.score = score
        p.rating = rating
        scores_data.append({"product": p.name, "score": score, "rating": rating})
    db.commit()

    # Segments
    sessions = db.query(ShopperSession).all()
    segments_data = []
    for s in sessions:
        result = classify_shopper(
            dwell_time=s.dwell_time,
            path_length=s.path_length,
            gaze_shifts=s.gaze_shifts
        )
        s.segment = result["segment"]
        segments_data.append({
            "shopper_id": s.id,
            "segment": result["segment"],
            "dwell_time": s.dwell_time
        })
    db.commit()

    # Recommendations
    rec_input = [
        {
            "name": p.name,
            "attention_duration": p.attention_duration,
            "pickup_rate": p.pickup_rate,
            "conversion_rate": p.conversion_rate,
            "interaction_frequency": p.interaction_frequency,
            "score": p.score
        }
        for p in products
    ]
    recommendations_data = [
        {"product": r["product"], "issue": r["issue"], "priority": r["priority"]}
        for r in generate_recommendations(rec_input)
    ]

    # Alerts
    alerts_data = [
        {"type": a["type"], "product": a["product"], "action": a["action"]}
        for a in check_alerts(scores_data)
    ]

    return {
        "scores": scores_data,
        "segments": segments_data,
        "recommendations": recommendations_data,
        "alerts": alerts_data,
    }


@router.get("/export/excel")
def export_excel_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download an Excel report with real data"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    data = gather_report_data(db)
    filepath = os.path.join(REPORTS_DIR, "report.xlsx")
    export_excel(data, filepath)
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="attention_report.xlsx"
    )


@router.get("/export/pdf")
def export_pdf_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download a PDF report with real data"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    data = gather_report_data(db)
    filepath = os.path.join(REPORTS_DIR, "report.pdf")
    export_pdf(data, filepath)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="attention_report.pdf"
    )