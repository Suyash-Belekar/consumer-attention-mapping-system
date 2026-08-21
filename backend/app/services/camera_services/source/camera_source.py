"""
source/camera_source.py

Single-responsibility wrapper around cv2.VideoCapture.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import cv2

from app.services.camera_services.config import CameraPipelineConfig
from app.services.camera_services.exceptions import CameraSourceError

logger = logging.getLogger(__name__)


class CameraSource:
    """Isolates OpenCV-specific quirks from the rest of the pipeline.

    Most notably: `isOpened()` can report True before the underlying
    driver is actually able to deliver frames. This class hides that
    behind a small, mockable interface so unit tests don't need real
    hardware.
    """

    def __init__(self, source: int | str, config: CameraPipelineConfig) -> None:
        self._source = source
        self._config = config
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        """Open the device and confirm it can actually deliver frames.

        Raises:
            CameraSourceError: if the source cannot be opened, or opens
                but never yields a frame within the warm-up budget.
        """
        self._cap = cv2.VideoCapture(self._source)

        if not self._cap.isOpened():
            raise CameraSourceError(
                f"Unable to open video source: {self._source!r}"
            )

        for attempt in range(1, self._config.warm_up_attempts + 1):
            success, _ = self._cap.read()

            if success:
                return

            logger.warning(
                "Camera not ready yet (attempt %d/%d) for source %r",
                attempt,
                self._config.warm_up_attempts,
                self._source,
            )
            time.sleep(self._config.warm_up_delay_seconds)

        self.release()
        raise CameraSourceError(
            f"Camera opened but never returned a frame: {self._source!r}"
        )

    def read(self):
        """Read the next frame. Mirrors cv2.VideoCapture.read()."""
        if self._cap is None:
            raise CameraSourceError("read() called before open().")
        return self._cap.read()

    def release(self) -> None:
        """Release the underlying capture device, if held. Idempotent."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()
