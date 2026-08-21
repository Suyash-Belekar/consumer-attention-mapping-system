<<<<<<< HEAD
from __future__ import annotations
import csv
from datetime import datetime,timedelta,timezone
from io import BytesIO,StringIO
from uuid import UUID
from fastapi import APIRouter,Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from sqlalchemy import func,select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database_models import AttentionSessionModel,ProductAttentionModel,ProductModel,ShelfModel
from app.services.product_scoring import build_store_references,calculate_attractiveness,recommendations
router=APIRouter(prefix="/api/reports",tags=["Reports & Exports"])
def _since(hours): return datetime.now(timezone.utc)-timedelta(hours=max(1,min(hours,720)))
async def _attention_rows(store_id,hours,db):
    rows=(await db.execute(select(ShelfModel.name.label("shelf_name"),func.count(func.distinct(AttentionSessionModel.tracker_id)).label("customers"),func.coalesce(func.sum(AttentionSessionModel.dwell_time_seconds),0).label("dwell")).outerjoin(AttentionSessionModel,(ShelfModel.id==AttentionSessionModel.shelf_id)&(AttentionSessionModel.entry_time>=_since(hours))).where(ShelfModel.store_id==store_id).group_by(ShelfModel.id,ShelfModel.name).order_by(ShelfModel.name.asc()))).all()
    return [{"shelf":r.shelf_name,"customers":int(r.customers or 0),"dwell_seconds":round(float(r.dwell or 0),2)} for r in rows]
async def _product_rows(store_id,db):
    rows=(await db.execute(select(ProductModel,ProductAttentionModel).join(ProductAttentionModel,ProductModel.id==ProductAttentionModel.product_id).where(ProductModel.store_id==store_id,ProductModel.is_active.is_(True)).order_by(ProductModel.name.asc()))).all(); refs=build_store_references([m for _,m in rows]); result=[]
    for product,metrics in rows:
        score,breakdown=calculate_attractiveness(metrics,refs); result.append({"product_id":str(product.id),"product":product.name,"attractiveness_score":score,"attention_duration":metrics.attention_duration,"interaction_freq":metrics.interaction_freq,"pickup_rate":metrics.pickup_rate,"conversion_rate":metrics.conversion_rate,"repeat_engagement":metrics.repeat_engagement,"recommendations":"; ".join(x["message"] for x in recommendations(metrics,breakdown))})
    return result
@router.get("/attention",dependencies=[Depends(get_current_user)])
async def attention_report(store_id:UUID,hours:int=24,db:AsyncSession=Depends(get_db)): return await _attention_rows(store_id,hours,db)
@router.get("/products",dependencies=[Depends(get_current_user)])
async def product_report(store_id:UUID,db:AsyncSession=Depends(get_db)): return await _product_rows(store_id,db)
@router.get("/attention.csv",dependencies=[Depends(get_current_user)])
async def attention_csv(store_id:UUID,hours:int=24,db:AsyncSession=Depends(get_db)):
    data=await _attention_rows(store_id,hours,db); b=StringIO(); w=csv.DictWriter(b,fieldnames=["shelf","customers","dwell_seconds"]); w.writeheader(); w.writerows(data); return StreamingResponse(iter([b.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=attention-report.csv"})
@router.get("/products.xlsx",dependencies=[Depends(get_current_user)])
async def products_xlsx(store_id:UUID,db:AsyncSession=Depends(get_db)):
    data=await _product_rows(store_id,db); wb=Workbook(); ws=wb.active; ws.title="Product Intelligence"; headers=["product_id","product","attractiveness_score","attention_duration","interaction_freq","pickup_rate","conversion_rate","repeat_engagement","recommendations"]; ws.append(headers)
    for row in data: ws.append([row[h] for h in headers])
    ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions; out=BytesIO(); wb.save(out); out.seek(0); return StreamingResponse(out,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=product-intelligence.xlsx"})
@router.get("/attention.pdf",dependencies=[Depends(get_current_user)])
async def attention_pdf(store_id:UUID,hours:int=24,db:AsyncSession=Depends(get_db)):
    data=await _attention_rows(store_id,hours,db); out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=landscape(A4),title="Consumer Attention Report"); rows=[["Shelf","Customers","Dwell Seconds"]]+[[r["shelf"],r["customers"],r["dwell_seconds"]] for r in data]; table=Table(rows,repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f2937")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.5,colors.grey),("PADDING",(0,0),(-1,-1),6)])); doc.build([table]); out.seek(0); return StreamingResponse(out,media_type="application/pdf",headers={"Content-Disposition":"attachment; filename=attention-report.pdf"})
=======
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
>>>>>>> 6edf5a418e08325876c687f139cebc0504528764
