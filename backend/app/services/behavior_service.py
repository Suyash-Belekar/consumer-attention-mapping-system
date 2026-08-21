from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_models import ShopperSessionModel
from app.schemas.schema import BehavioralSegment


def classify_shopper_archetype(path_length: float, dwell_time: float, gaze_shifts: int) -> BehavioralSegment:
    """Classify a completed shopper trajectory into the Milestone 3 archetypes."""
    if gaze_shifts >= 8 and path_length < 50.0:
        return BehavioralSegment.COMPARISON_SHOPPER
    if path_length >= 50.0 and dwell_time >= 600.0:
        return BehavioralSegment.EXPLORER
    if path_length < 50.0 and dwell_time <= 120.0:
        return BehavioralSegment.QUICK_BUYER
    return BehavioralSegment.IMPULSE_BUYER


async def log_and_classify_session(
    db: AsyncSession,
    session_id: UUID,
    path_length: float,
    dwell_time: float,
    gaze_shifts: int,
) -> ShopperSessionModel:
    """Update an existing completed shopper session with its behavioral segment."""
    record = await db.scalar(select(ShopperSessionModel).where(ShopperSessionModel.session_id == session_id))
    if record is None:
        raise ValueError("Shopper session does not exist. Persist the completed tracking session before classification.")

    record.path_length = path_length
    record.total_dwell_time = dwell_time
    record.head_gaze_shifts = gaze_shifts
    record.behavioral_segment = classify_shopper_archetype(path_length, dwell_time, gaze_shifts).value
    await db.commit()
    await db.refresh(record)
    return record
