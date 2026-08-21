"""Backward-compatible facade for the canonical domain dwell service.

All runtime dwell state is owned by ``app.analytics.domain.dwell``. This
module exists only so older analytics imports keep working during the
migration to the domain-driven architecture.
"""

from __future__ import annotations

from typing import List

from app.ai.tracker import TrackedPerson
from app.analytics.domain.dwell.dwell_models import DwellRecord
from app.analytics.domain.dwell.dwell_policy import DwellPolicy
from app.analytics.domain.dwell.services.dwell_service import DwellService


class DwellTimeManager(DwellService):
    """Compatibility adapter backed by the canonical DwellService."""

    def __init__(self, policy: DwellPolicy | None = None) -> None:
        super().__init__(policy=policy or DwellPolicy())

    @property
    def active_sessions(self) -> dict[int, DwellRecord]:
        return self._sessions.active_sessions

    @property
    def completed_sessions(self) -> list[DwellRecord]:
        return self.get_completed_sessions()

    def update(self, tracked_people: List[TrackedPerson]) -> None:
        super().update(tracked_people)

    def get_active_records(self) -> list[DwellRecord]:
        return self.get_active_sessions()

    def clear_completed_sessions(self) -> None:
        self.clear_completed_sessions_domain()

    def clear_completed_sessions_domain(self) -> None:
        super().clear_completed_sessions()

    def export_completed_sessions(self):
        return self.export_completed_sessions_domain()

    def export_completed_sessions_domain(self):
        return super().export_completed_sessions()

    def print_summary(self) -> None:
        for session in self.get_active_sessions():
            print(f"ID {session.track_id:<4} Dwell: {session.dwell_time:.2f}s")

    def print_completed_sessions(self) -> None:
        for session in self.get_completed_sessions():
            print(
                f"Track ID: {session.track_id}\n"
                f"Entry: {session.entry_time:.2f}\n"
                f"Exit: {session.exit_time:.2f}\n"
                f"Dwell: {session.dwell_time:.2f}s"
            )

    def total_active_sessions(self) -> int:
        return self.active_count

    def total_completed_sessions(self) -> int:
        return self.completed_count
