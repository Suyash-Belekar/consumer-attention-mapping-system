from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import cv2

from app.ai.detector import PersonDetector
from app.ai.frame_processor import FrameProcessor
from app.ai.models import FrameData, TrackedPerson
from app.ai.tracker import PersonTracker


@dataclass(slots=True)
class FramePipelineResult:
    frame: Any
    tracked_people: list[TrackedPerson]
    detections: list
    metadata: dict[str, Any]


class FramePipeline:
    """Single-pass frame pipeline.

    ``FrameProcessor`` owns detection, tracking, gaze and dwell updates. The
    pipeline consumes those results instead of running YOLO/ByteTrack a second
    time. This removes the duplicate inference path that previously depressed
    camera FPS.
    """

    def __init__(self, processor: FrameProcessor, detector: PersonDetector | None = None, tracker: PersonTracker | None = None) -> None:
        self._processor = processor
        self._detector = detector
        self._tracker = tracker

    def process(self, frame: Any, frame_number: int, stream_start: float) -> FramePipelineResult:
        processor_output = self._processor.process(
            frame=frame,
            frame_number=frame_number,
            stream_start=stream_start,
        )

        if isinstance(processor_output, FrameData):
            processed_frame = processor_output.frame
            detections = processor_output.detections
            tracked_people = processor_output.tracked_people
            timestamp = processor_output.timestamp
            metadata = dict(processor_output.metadata)
        else:
            processed_frame = processor_output
            detections = []
            tracked_people = []
            timestamp = max(0.0, time.time() - stream_start)
            metadata = {}

        metadata.update({
            "frame_number": frame_number,
            "timestamp": timestamp,
            "fps": frame_number / timestamp if timestamp > 0 else 0.0,
            "detections": len(detections),
            "tracks": len(tracked_people),
        })

        return FramePipelineResult(
            frame=processed_frame,
            tracked_people=tracked_people,
            detections=detections,
            metadata=metadata,
        )

    def draw_tracks(self, frame: Any, tracked_people: list[TrackedPerson]) -> Any:
        if self._tracker is not None:
            return self._tracker.draw_tracks(frame, tracked_people)
        return self._processor.tracker.draw_tracks(frame, tracked_people)
