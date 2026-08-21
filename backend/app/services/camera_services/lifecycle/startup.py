"""
lifecycle/startup.py

Everything needed to bring a CameraPipeline from constructed to
running: opening the camera source and printing the startup banner.
"""

from __future__ import annotations

import logging
import time

from app.services.camera_services.config import CameraPipelineConfig
from app.services.camera_services.exceptions import CameraSourceError
from app.services.camera_services.source.camera_source import CameraSource

logger = logging.getLogger(__name__)


def start_camera(camera: CameraSource) -> float:
    """Open the camera source and return the stream start timestamp.

    Raises:
        CameraSourceError: propagated from CameraSource.open() if the
            source cannot be opened or warmed up.
    """
    camera.open()
    logger.info("Camera initialized successfully.")
    return time.perf_counter()


def print_banner(config: CameraPipelineConfig) -> None:
    """Print the console startup banner."""
    width = 60
    print("=" * width)
    print(config.banner_title)
    print("=" * width)
    print("\nPress 'Q' to quit.\n")
