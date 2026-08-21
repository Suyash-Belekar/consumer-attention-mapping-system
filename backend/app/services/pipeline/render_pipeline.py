"""
render_pipeline.py

Consumer Attention Mapping System

Render Pipeline

Responsibilities
----------------
- Draw tracker overlays
- Draw analytics overlays
- Draw performance information

This module does NOT:
- Detect people
- Track people
- Calculate analytics
- Display frames
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import cv2

from app.ai.tracker import PersonTracker
from app.services.pipeline.analytics_pipeline import (
    AnalyticsPipeline,
    AnalyticsPipelineResult,
)

logger = logging.getLogger(__name__)


# ==========================================================
# Render Configuration
# ==========================================================

@dataclass(slots=True)
class RenderConfig:
    """
    Rendering configuration.
    """

    show_tracking: bool = True

    show_dwell_time: bool = True

    show_statistics: bool = True

    show_fps: bool = True


# ==========================================================
# Render Pipeline
# ==========================================================

class RenderPipeline:
    """
    Responsible for rendering all overlays.
    """

    def __init__(
        self,
        tracker: PersonTracker,
        analytics: AnalyticsPipeline,
        config: Optional[RenderConfig] = None,
    ) -> None:

        self._tracker = tracker

        self._analytics = analytics

        self._config = config or RenderConfig()

    # ======================================================
    # Main Renderer
    # ======================================================

    def render(
        self,
        frame,
        analytics_result: AnalyticsPipelineResult,
        fps: float,
    ):
        """
        Render every overlay.
        """

        if self._config.show_tracking:

            frame = self._tracker.draw_tracks(

                frame,

                analytics_result.tracked_people,

            )

        if self._config.show_dwell_time:

            self._draw_dwell_time(

                frame,

                analytics_result,

            )

        if self._config.show_statistics:

            self._draw_statistics(

                frame,

                analytics_result,

            )

        if self._config.show_fps:

            self._draw_fps(

                frame,

                fps,

            )

        return frame

    # ======================================================
    # Private Rendering Methods
    # ======================================================

    def _draw_dwell_time(
        self,
        frame,
        analytics_result: AnalyticsPipelineResult,
    ) -> None:
        """
        Draw shopper dwell time.
        """

        for person in analytics_result.tracked_people:

            dwell = self._analytics.get_dwell_time(

                person.track_id

            )

            x1, y1, _, _ = person.bbox

            cv2.putText(

                frame,

                f"Dwell: {dwell:.1f}s",

                (x1, y1 + 20),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (0, 255, 255),

                2,

            )

    def _draw_statistics(
        self,
        frame,
        analytics_result: AnalyticsPipelineResult,
    ) -> None:
        """
        Draw analytics statistics.
        """

        cv2.putText(

            frame,

            f"Active : {analytics_result.active_sessions}",

            (20, 35),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 0),

            2,

        )

        cv2.putText(

            frame,

            f"Completed : {analytics_result.completed_sessions}",

            (20, 65),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 0),

            2,

        )

    def _draw_fps(
        self,
        frame,
        fps: float,
    ) -> None:
        """
        Draw FPS.
        """

        cv2.putText(

            frame,

            f"FPS : {fps:.2f}",

            (20, 95),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 165, 255),

            2,

        )