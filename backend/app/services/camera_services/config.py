"""
config.py

Tunable, environment-independent settings for CameraPipeline.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CameraPipelineConfig:
    """Explicit config instead of scattered magic numbers.

    Keeps the pipeline testable — e.g. inject `warm_up_attempts=0` in a
    unit test with a fake source — and easy to tune per deployment (a
    flaky RTSP stream needs a longer warm-up budget than a local USB
    webcam).
    """

    processed_size: tuple[int, int] = (640, 640)
    warm_up_attempts: int = 10
    warm_up_delay_seconds: float = 0.1
    banner_title: str = "Consumer Attention Mapping System"
