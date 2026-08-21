from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DisplayConfig:
    window_name: str = "Consumer Attention Mapping System"
    fullscreen: bool = False
    resizable: bool = True
    enabled: bool = False


class DisplayPipeline:
    """Optional OpenCV GUI layer. Disabled by default for API/Docker runtimes."""

    def __init__(self, config: DisplayConfig | None = None) -> None:
        self._config = config or DisplayConfig()
        self._initialized = False
        if self._config.enabled:
            self._initialize_window()

    def _initialize_window(self) -> None:
        flag = cv2.WINDOW_NORMAL if self._config.resizable else cv2.WINDOW_AUTOSIZE
        cv2.namedWindow(self._config.window_name, flag)
        if self._config.fullscreen:
            cv2.setWindowProperty(self._config.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        self._initialized = True

    def show(self, frame) -> None:
        if self._initialized:
            cv2.imshow(self._config.window_name, frame)

    def poll_key(self) -> int:
        if not self._initialized:
            return -1
        return cv2.waitKey(1) & 0xFF

    def should_exit(self) -> bool:
        return self.poll_key() == ord("q")

    def close(self) -> None:
        if self._initialized:
            cv2.destroyWindow(self._config.window_name)
            self._initialized = False
