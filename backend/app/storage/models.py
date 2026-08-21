"""
storage/models.py

Storage models used by the persistence layer.
These models mirror the database schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AttentionSession:
    """
    Storage model representing a row in the
    attention_sessions table.
    """

    store_id: int
    shelf_id: int | None

    tracker_id: int

    entry_time: datetime
    exit_time: datetime

    dwell_time_seconds: float