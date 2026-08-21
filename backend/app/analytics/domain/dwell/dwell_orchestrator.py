import logging
from typing import List

from app.ai.tracker import TrackedPerson

from app.analytics.domain.dwell.services.dwell_service import (
    DwellService,
)


logger = logging.getLogger(__name__)


class DwellOrchestrator:
    """
    High level coordinator for dwell analytics.
    """


    def __init__(
        self,
        dwell_service: DwellService,
    ) -> None:

        self._dwell_service = dwell_service



    def process(
        self,
        tracked_people: List[TrackedPerson],
        timestamp: float = 0.0,
    ) -> None:
        """
        Process one frame of tracking data.
        """
        self._dwell_service.update(
            tracked_people=tracked_people,
            current_time=timestamp,
        )

    @property
    def active_count(self) -> int:
        return self._dwell_service.active_count

    @property
    def completed_count(self) -> int:
        return self._dwell_service.completed_count

    def get_dwell_time(self, track_id: int) -> float:
        return self._dwell_service.get_dwell_time(track_id)

    def get_active_sessions(self):
        return self._dwell_service.get_active_sessions()

    def get_completed_sessions(self):
        return self._dwell_service.get_completed_sessions()

    def clear_completed_sessions(self) -> None:
        self._dwell_service.clear_completed_sessions()

    def reset(self) -> None:
        self._dwell_service.reset()
