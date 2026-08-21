from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DwellPolicy:
    """
    Configuration for the Dwell Analytics subsystem.

    These values define how the DwellTimeManager behaves
    during real-time shopper tracking.
    """

    # --------------------------------------------------
    # Session Lifecycle
    # --------------------------------------------------

    #: Seconds a shopper may disappear before the session
    #: is considered finished.
    exit_timeout: float = 1.0

    #: Ignore extremely short sessions caused by
    #: false detections.
    minimum_dwell_time: float = 0.50

    # --------------------------------------------------
    # Tracking Stability
    # --------------------------------------------------

    #: Number of consecutive frames a shopper may be
    #: absent before timing logic is evaluated.
    max_missing_frames: int = 30

    #: Minimum confidence required for a tracked person
    #: to participate in dwell analytics.
    minimum_tracking_confidence: float = 0.50

    # --------------------------------------------------
    # Runtime Behaviour
    # --------------------------------------------------

    #: Automatically remove exported completed sessions.
    auto_clear_completed: bool = False

    #: Generate runtime statistics after every update.
    enable_statistics: bool = True

    #: Enable detailed debug logging.
    enable_debug_logging: bool = False

    # --------------------------------------------------
    # Performance
    # --------------------------------------------------

    #: Initial capacity hint for active session storage.
    expected_max_active_sessions: int = 100

    #: Maximum completed sessions kept in memory before
    #: synchronization should occur.
    completed_session_buffer: int = 1000