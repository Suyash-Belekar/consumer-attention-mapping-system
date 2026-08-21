from __future__ import annotations

import time
from typing import Any

import cv2
import numpy as np

from app.ai.detector import PersonDetector
from app.ai.models import FrameData
from app.ai.tracker import ByteTrackerEngine
from app.analytics.domain.attention.cv.gaze_projection import HeadPoseGazeEstimator
from app.services.mapping_service import point_in_polygon


class FrameProcessor:
    """Single CV pass: detect -> track -> map -> estimate attention."""

    def __init__(
        self,
        shelves_config: dict[Any, Any] | None = None,
        zones_config: dict[Any, Any] | None = None,
        products_config: dict[Any, Any] | None = None,
        store_id: object | None = None,
        camera_id: str | None = None,
        detector: PersonDetector | None = None,
        tracker: ByteTrackerEngine | None = None,
        gaze_estimator: HeadPoseGazeEstimator | None = None,
    ) -> None:
        self.detector = detector or PersonDetector()
        self.tracker = tracker or ByteTrackerEngine()
        self.gaze_estimator = gaze_estimator or HeadPoseGazeEstimator()
        self.store_id = store_id
        self.camera_id = camera_id
        self.shelves_config = shelves_config or {}
        self.zones_config = zones_config or {}
        self.products_config = products_config or {}

    @staticmethod
    def _contains(x: float, y: float, mapping: Any) -> bool:
        polygon = mapping.get("polygon") if isinstance(mapping, dict) else mapping
        if polygon and point_in_polygon(x, y, polygon):
            return True
        bbox = mapping.get("bbox") if isinstance(mapping, dict) else None
        if bbox and len(bbox) == 4:
            return float(bbox[0]) <= x <= float(bbox[2]) and float(bbox[1]) <= y <= float(bbox[3])
        return False

    def _resolve_context(self, x: float, y: float) -> tuple[Any, Any, Any]:
        zone_id = next((key for key, value in self.zones_config.items() if self._contains(x, y, value)), None)
        shelf_id = next((key for key, value in self.shelves_config.items() if self._contains(x, y, value)), None)
        product_id = next((key for key, value in self.products_config.items() if self._contains(x, y, value)), None)
        return zone_id, shelf_id, product_id

    def _resolve_gaze_shelf(self, x: float, y: float) -> Any:
        return next((key for key, value in self.shelves_config.items() if self._contains(x, y, value)), None)

    def process(
        self,
        frame: np.ndarray,
        store_id: object | None = None,
        repo: object | None = None,
        frame_number: int = 0,
        stream_start: float | None = None,
        **kwargs: Any,
    ) -> FrameData:
        effective_store_id = store_id if store_id is not None else self.store_id
        frame_h, frame_w = frame.shape[:2]
        timestamp = time.time()
        stream_elapsed = max(0.0, time.perf_counter() - stream_start) if stream_start is not None else 0.0

        detections = self.detector.detect(frame)
        tracked_shoppers = []

        if detections:
            tracked_shoppers = self.tracker.update(detections, timestamp=timestamp)

            for shopper in tracked_shoppers:
                shopper.store_id = effective_store_id
                shopper.camera_id = self.camera_id
                cx, cy = shopper.center
                zone_id, shelf_id, product_id = self._resolve_context(cx, cy)
                shopper.zone_id = zone_id
                shopper.shelf_id = shelf_id
                shopper.product_id = product_id

                px1, py1, px2, py2 = map(int, shopper.bbox)
                cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {shopper.track_id}", (px1, max(15, py1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                head_h = max(10, int((py2 - py1) * 0.35))
                hx1, hy1 = max(0, px1), max(0, py1)
                hx2, hy2 = min(frame_w, px2), min(frame_h, py1 + head_h)
                gaze_point = None

                if (hx2 - hx1) > 10 and (hy2 - hy1) > 10:
                    head_crop = frame[hy1:hy2, hx1:hx2]
                    estimator_output = self.gaze_estimator.estimate_head_pose(frame, head_crop)
                    if estimator_output is not None:
                        local_gaze, landmarks_2d = estimator_output
                        if local_gaze is not None:
                            gaze_point = (hx1 + local_gaze[0], hy1 + local_gaze[1])
                        if landmarks_2d is not None and len(landmarks_2d) > 0:
                            fx1 = hx1 + int(np.min(landmarks_2d[:, 0]))
                            fy1 = hy1 + int(np.min(landmarks_2d[:, 1]))
                            fx2 = hx1 + int(np.max(landmarks_2d[:, 0]))
                            fy2 = hy1 + int(np.max(landmarks_2d[:, 1]))
                            cv2.rectangle(frame, (fx1, fy1), (fx2, fy2), (0, 255, 255), 1)
                            nose = (hx1 + int(landmarks_2d[0][0]), hy1 + int(landmarks_2d[0][1]))
                            if gaze_point is not None:
                                gaze_shelf = self._resolve_gaze_shelf(*gaze_point)
                                if gaze_shelf is not None:
                                    shopper.shelf_id = gaze_shelf
                                cv2.arrowedLine(frame, nose, gaze_point, (0, 255, 0) if gaze_shelf is not None else (0, 0, 255), 2, tipLength=0.2)

        return FrameData(
            frame=frame,
            frame_number=frame_number,
            timestamp=timestamp,
            detections=detections or [],
            tracked_people=tracked_shoppers,
            metadata={
                "store_id": effective_store_id,
                "camera_id": self.camera_id,
                "tracked_people": len(tracked_shoppers),
                "stream_elapsed_seconds": stream_elapsed,
            },
        )
