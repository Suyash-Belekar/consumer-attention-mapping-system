from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database_models import AlertModel
from app.schemas.management import AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=list[AlertResponse], dependencies=[Depends(get_current_user)])
async def list_alerts(store_id: UUID | None = None, unread_only: bool = False, db: AsyncSession = Depends(get_db)):
    stmt = select(AlertModel).order_by(AlertModel.created_at.desc()).limit(200)
    if store_id: stmt = stmt.where(AlertModel.store_id == store_id)
    if unread_only: stmt = stmt.where(AlertModel.is_read.is_(False))
    return (await db.execute(stmt)).scalars().all()

@router.post("/{alert_id}/read", response_model=AlertResponse, dependencies=[Depends(get_current_user)])
async def mark_read(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    alert = await db.get(AlertModel, alert_id)
    if not alert: raise HTTPException(404, "Alert not found.")
    alert.is_read = True; await db.commit(); await db.refresh(alert); return alert
