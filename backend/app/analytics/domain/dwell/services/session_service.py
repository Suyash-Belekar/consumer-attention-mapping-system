from __future__ import annotations

import time
from collections import deque
from typing import Deque, Any

from app.ai.models import TrackedPerson
from app.analytics.domain.dwell.dwell_models import DwellRecord
from app.analytics.domain.dwell.dwell_policy import DwellPolicy


class SessionManager:
    """Manages the lifecycle of shopper dwell sessions.

    Responsibilities
    ----------------
    - Create new shopper sessions
    - Update dwell time
    - Detect exits
    - Queue completed sessions
    - Expose session information to higher layers

    This class owns ONLY session state.
    """

    def __init__(
        self,
        policy: DwellPolicy,
    ) -> None:
        self._policy = policy
        self._active_sessions: dict[int, DwellRecord] = {}
        self._completed_sessions: Deque[DwellRecord] = deque(
            maxlen=policy.completed_session_buffer,
        )

    # ==========================================================
    # Public API
    # ==========================================================

    def update(
        self,
        tracked_people: list[TrackedPerson],
        current_time: float | None = None,
    ) -> None:
        """Update all shopper sessions for the current frame."""
        now = current_time if current_time is not None else time.time()
        visible_ids = {person.track_id for person in tracked_people}

        self._update_visible_people(tracked_people, now)
        self._expire_missing_people(visible_ids, now)

    def update_shopper_state(
        self,
        shopper_id: int,
        store_id: int | None = None,
        shelf_id: Any | None = None,
        camera_id: str | None = None,
        zone_id: Any | None = None,
        current_time: float | None = None,
    ) -> None:
        """Update or create a dwell session state for a single shopper safely."""
        now = current_time if current_time is not None else time.time()
        session = self._active_sessions.get(shopper_id)

        if session is None:
            session = DwellRecord(
                track_id=shopper_id,
                entry_time=now,
                last_seen=now,
            )
            self._active_sessions[shopper_id] = session

        session.last_seen = now
        session.dwell_time = max(0.0, now - session.entry_time)

        # Slot-safe attribute assignment
        for attr, val in (("store_id", store_id), ("shelf_id", shelf_id), ("camera_id", camera_id), ("zone_id", zone_id)):
            if val is not None and hasattr(session, attr):
                try:
                    setattr(session, attr, val)
                except AttributeError:
                    pass

    def expire_absent_sessions(
        self,
        present_shopper_ids: set[int],
        current_time: float | None = None,
    ) -> list[DwellRecord]:
        """Expires/closes active sessions for shoppers no longer present in the frame.

        Returns any newly completed DwellRecords immediately.
        """
        now = current_time if current_time is not None else time.time()
        self._expire_missing_people(present_shopper_ids, now)
        return self.pop_completed_sessions()

    # ==========================================================
    # Visible & Missing Handlers
    # ==========================================================

    def _update_visible_people(
        self,
        tracked_people: list[TrackedPerson],
        now: float,
    ) -> None:
        for person in tracked_people:
            if person.confidence < self._policy.minimum_tracking_confidence:
                continue

            session = self._active_sessions.get(person.track_id)

            if session is None:
                session = DwellRecord(
                    track_id=person.track_id,
                    entry_time=now,
                    last_seen=now,
                )
                self._active_sessions[person.track_id] = session
            else:
                session.last_seen = now
            session.store_id = getattr(person, "store_id", None)
            session.camera_id = getattr(person, "camera_id", None)
            session.zone_id = getattr(person, "zone_id", None)
            session.shelf_id = getattr(person, "shelf_id", None)
            session.product_id = getattr(person, "product_id", None)

            session.dwell_time = max(0.0, now - session.entry_time)

    def _expire_missing_people(
        self,
        visible_ids: set[int],
        now: float,
    ) -> None:
        expired: list[int] = []

        for track_id, session in self._active_sessions.items():
            if track_id in visible_ids:
                continue

            disappeared_for = now - session.last_seen

            if disappeared_for < self._policy.exit_timeout:
                continue

            session.exit_time = session.last_seen
            session.dwell_time = max(0.0, session.exit_time - session.entry_time)

            if hasattr(session, "active"):
                session.active = False

            if session.dwell_time >= self._policy.minimum_dwell_time:
                self._completed_sessions.append(session)

            expired.append(track_id)

        for track_id in expired:
            del self._active_sessions[track_id]

    # ==========================================================
    # Queries & Exports
    # ==========================================================

    def get_active_records(self) -> list[DwellRecord]:
        return list(self._active_sessions.values())

    def get_completed_records(self) -> list[DwellRecord]:
        return list(self._completed_sessions)

    def get_dwell_time(self, track_id: int) -> float:
        session = self._active_sessions.get(track_id)
        return session.dwell_time if session else 0.0

    def pop_completed_sessions(self) -> list[DwellRecord]:
        """Return completed sessions and clear the queue."""
        records = list(self._completed_sessions)
        self._completed_sessions.clear()
        return records

    def clear_completed(self) -> None:
        """Clear completed session queue."""
        self._completed_sessions.clear()

    # ==========================================================
    # Properties & Lifecycle
    # ==========================================================

    @property
    def active_count(self) -> int:
        return len(self._active_sessions)

    @property
    def completed_count(self) -> int:
        return len(self._completed_sessions)

    @property
    def active_sessions(self) -> dict[int, DwellRecord]:
        return dict(self._active_sessions)

    def reset(self) -> None:
        """Reset all session state."""
        self._active_sessions.clear()
        self._completed_sessions.clear()