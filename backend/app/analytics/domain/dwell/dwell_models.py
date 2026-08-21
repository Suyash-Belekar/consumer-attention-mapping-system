from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict


# ==========================================================
# Dwell Session Record
# ==========================================================


@dataclass(slots=True)
class DwellRecord:
    """
    Represents a single shopper dwell session.

    Lifecycle
    ---------
    ACTIVE
        Shopper currently detected.

    COMPLETED
        Shopper exited tracking area.
    """

    track_id: int

    entry_time: float

    last_seen: float

    exit_time: Optional[float] = None

    dwell_time: float = 0.0

    active: bool = True
    store_id: object | None = None
    camera_id: str | None = None
    zone_id: object | None = None
    shelf_id: object | None = None
    product_id: object | None = None


    @property
    def person_id(self) -> int:
        """
        Backward compatibility alias.

        Older modules may use person_id.
        """
        return self.track_id


    def close(self, timestamp: float):
        """
        Mark session as completed.
        """

        self.exit_time = timestamp
        self.dwell_time = timestamp - self.entry_time
        self.active = False



# ==========================================================
# Completed Session Export Model
# ==========================================================


@dataclass(slots=True)
class CompletedDwellRecord:
    """
    Represents finalized dwell session data.

    Used for:
    - Database storage
    - Analytics export
    - Reporting
    """

    track_id: int

    entry_time: float

    exit_time: float

    dwell_time: float



# ==========================================================
# Runtime Snapshot
# ==========================================================


@dataclass(slots=True)
class DwellSnapshot:
    """
    Current runtime analytics snapshot.

    Generated after frame processing.
    """

    timestamp: float = 0.0

    active_sessions: int = 0

    completed_sessions: int = 0

    average_dwell_time: float = 0.0

    maximum_dwell_time: float = 0.0

    minimum_dwell_time: float = 0.0

    total_dwell_time: float = 0.0



# ==========================================================
# Dwell Statistics
# ==========================================================


@dataclass(slots=True)
class DwellStatistics:
    """
    Aggregated analytics statistics.

    Used by:
    - Dashboard
    - Reports
    - API responses
    """

    total_sessions: int = 0

    active_sessions: int = 0

    completed_sessions: int = 0

    average_dwell_time: float = 0.0

    maximum_dwell_time: float = 0.0

    minimum_dwell_time: float = 0.0

    total_dwell_time: float = 0.0


# ==========================================================
# Manager State
# ==========================================================


@dataclass(slots=True)
class DwellState:

    """
    Public state exposed by DwellManager.

    Prevents external modules from
    accessing internal session dictionaries.
    """

    active_count: int = 0

    completed_count: int = 0

    timestamp: float = 0.0

    snapshot: DwellSnapshot = field(
        default_factory=DwellSnapshot
    )



# ==========================================================
# Configuration Model
# ==========================================================


@dataclass(slots=True)
class DwellConfig:
    """
    Configuration for dwell analytics.
    """

    exit_timeout: float = 2.0

    minimum_dwell_time: float = 1.0

    maximum_history: int = 10000



# ==========================================================
# Manager Internal Storage
# ==========================================================


@dataclass(slots=True)
class DwellStorage:

    """
    Internal storage container.

    Used by DwellManager.

    Keeps implementation details isolated.
    """

    active_sessions: Dict[int, DwellRecord] = field(
        default_factory=dict
    )

    completed_sessions: list[CompletedDwellRecord] = field(
        default_factory=list
    )