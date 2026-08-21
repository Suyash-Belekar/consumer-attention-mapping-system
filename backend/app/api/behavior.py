from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schema import BehavioralTagRequest, BehavioralTagResponse
from app.services.behavior_service import log_and_classify_session

router = APIRouter(prefix="/api/behavior", tags=["Behavior Intelligence"])


@router.post("/tag-session", response_model=BehavioralTagResponse, dependencies=[Depends(get_current_user)])
async def tag_shopper_session(payload: BehavioralTagRequest, db: AsyncSession = Depends(get_db)):
    try:
        updated = await log_and_classify_session(
            db=db,
            session_id=UUID(payload.session_id),
            path_length=payload.path_length,
            dwell_time=payload.total_dwell_time,
            gaze_shifts=payload.head_gaze_shifts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return BehavioralTagResponse(
        session_id=str(updated.session_id),
        behavioral_segment=updated.behavioral_segment,
        updated_at=updated.created_at,
    )
