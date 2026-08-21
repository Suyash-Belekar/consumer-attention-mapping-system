from __future__ import annotations

import abc
import logging
from typing import List, Optional, Tuple

import cv2
import numpy as np
import supervision as sv

from app.ai.models import Detection, TrackedPerson

logger = logging.getLogger(__name__)


class _BaseTrackerAdapter(abc.ABC):
    """Abstract interface for ByteTrack backends."""

    @abc.abstractmethod
    def update(self, detections: sv.Detections) -> sv.Detections:
        """Update tracker state and return updated Detections with tracker_id."""
        pass


class _StandaloneTrackerAdapter(_BaseTrackerAdapter):
    """Adapter for the standalone `trackers` package (ByteTrackTracker)."""

    def __init__(self) -> None:
        from trackers import ByteTrackTracker

        self._tracker = ByteTrackTracker()

    def update(self, detections: sv.Detections) -> sv.Detections:
        return self._tracker.update(detections)


class _SupervisionTrackerAdapter(_BaseTrackerAdapter):
    """Adapter for native supervision.ByteTrack with version fallback support."""

    def __init__(
        self,
        activation_threshold: float,
        lost_track_buffer: int,
        matching_threshold: float,
        frame_rate: int,
    ) -> None:
        self._tracker = sv.ByteTrack(
            track_activation_threshold=activation_threshold,
            lost_track_buffer=lost_track_buffer,
            minimum_matching_threshold=matching_threshold,
            frame_rate=frame_rate,
        )

    def update(self, detections: sv.Detections) -> sv.Detections:
        # Supervision 0.28+ renamed update_with_detections() to update()
        if hasattr(self._tracker, "update"):
            return self._tracker.update(detections)
        return self._tracker.update_with_detections(detections)


class PersonTracker:
    """Stateful Person Tracker wrapping ByteTrack.
    
    Maintains track identity across frame sequences for active shoppers.
    """

    DEFAULT_ACTIVATION_THRESHOLD: float = 0.20
    DEFAULT_LOST_TRACK_BUFFER: int = 60
    DEFAULT_MATCHING_THRESHOLD: float = 0.50
    DEFAULT_FRAME_RATE: int = 30

    def __init__(
        self,
        frame_rate: Optional[float] = None,
        activation_threshold: Optional[float] = None,
        lost_track_buffer: Optional[int] = None,
        matching_threshold: Optional[float] = None,
    ) -> None:
        self.activation = (
            activation_threshold
            if activation_threshold is not None
            else self.DEFAULT_ACTIVATION_THRESHOLD
        )
        self.lost_buffer = (
            lost_track_buffer
            if lost_track_buffer is not None
            else self.DEFAULT_LOST_TRACK_BUFFER
        )
        self.matching = (
            matching_threshold
            if matching_threshold is not None
            else self.DEFAULT_MATCHING_THRESHOLD
        )
        self.fps = (
            int(frame_rate)
            if frame_rate and frame_rate > 0
            else self.DEFAULT_FRAME_RATE
        )

        self._backend: _BaseTrackerAdapter = self._initialize_backend()

    def _initialize_backend(self) -> _BaseTrackerAdapter:
        try:
            adapter = _StandaloneTrackerAdapter()
            logger.info("Initialized PersonTracker using `trackers.ByteTrackTracker`")
            return adapter
        except ImportError:
            adapter = _SupervisionTrackerAdapter(
                activation_threshold=self.activation,
                lost_track_buffer=self.lost_buffer,
                matching_threshold=self.matching,
                frame_rate=self.fps,
            )
            logger.info("Initialized PersonTracker using `supervision.ByteTrack`")
            return adapter

    def update(
        self,
        detections: List[Detection],
        timestamp: float,
        frame_rate: Optional[float] = None,
    ) -> List[TrackedPerson]:
        """Ingest current frame detections and yield stateful TrackedPerson entities."""
        if not detections:
            return []

        # Vectorized conversion to Supervision format
        boxes = np.empty((len(detections), 4), dtype=np.float32)
        confidences = np.empty(len(detections), dtype=np.float32)
        class_ids = np.empty(len(detections), dtype=np.int32)

        for idx, det in enumerate(detections):
            boxes[idx] = det.bbox
            confidences[idx] = det.confidence
            class_ids[idx] = det.class_id

        sv_detections = sv.Detections(
            xyxy=boxes,
            confidence=confidences,
            class_id=class_ids,
        )

        tracked = self._backend.update(sv_detections)

        if tracked.tracker_id is None or len(tracked.tracker_id) == 0:
            return []

        return [
            TrackedPerson(
                track_id=int(tid),
                bbox=(int(b[0]), int(b[1]), int(b[2]), int(b[3])),
                confidence=float(conf),
                timestamp=timestamp,
            )
            for b, conf, tid in zip(
                tracked.xyxy, tracked.confidence, tracked.tracker_id
            )
        ]

    def draw_tracks(
        self,
        frame: np.ndarray,
        tracked_people: List[TrackedPerson],
        inplace: bool = False,
    ) -> np.ndarray:
        """Draw bounding boxes and labels for tracked shoppers on the frame."""
        return ShopperVisualizer.draw_tracks(
            frame=frame, tracked_people=tracked_people, inplace=inplace
        )

    # Alias for draw_tracks to preserve compatibility across modules
    draw_detections = draw_tracks

    @staticmethod
    def get_active_track_ids(tracked_people: List[TrackedPerson]) -> List[int]:
        return [person.track_id for person in tracked_people]


class ShopperVisualizer:
    """Utility class handling frame annotation overlays for tracked shoppers."""

    BOX_COLOR: Tuple[int, int, int] = (0, 255, 128)  # Emerald Green
    LABEL_BG_COLOR: Tuple[int, int, int] = (0, 180, 90)
    TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)

    @classmethod
    def draw_tracks(
        cls,
        frame: np.ndarray,
        tracked_people: List[TrackedPerson],
        inplace: bool = False,
    ) -> np.ndarray:
        if frame is None or frame.size == 0 or not tracked_people:
            return frame

        annotated = frame if inplace else frame.copy()
        img_h, img_w = annotated.shape[:2]

        for person in tracked_people:
            x1, y1, x2, y2 = person.bbox

            # Clamp bounding box coordinates to image dimensions
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img_w, x2), min(img_h, y2)

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                cls.BOX_COLOR,
                thickness=2,
            )

            label = f"Shopper #{person.track_id}"
            (w, h), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.55,
                thickness=2,
            )

            label_y1 = max(0, y1 - h - 8)
            label_y2 = y1

            # Background rectangle for text
            cv2.rectangle(
                annotated,
                (x1, label_y1),
                (min(img_w, x1 + w + 12), label_y2),
                cls.LABEL_BG_COLOR,
                thickness=-1,
            )

            # Header text string
            cv2.putText(
                annotated,
                label,
                (x1 + 6, max(label_y2 - 4, 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                cls.TEXT_COLOR,
                thickness=2,
                lineType=cv2.LINE_AA,
            )

        return annotated


# Legacy Aliases
ByteTrackerEngine = PersonTracker
ShopperTracker = PersonTracker