"""
lifecycle/shutdown.py

Everything needed to bring a CameraPipeline from running to fully
released: closing the camera/db/display and flushing background sync.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.services.camera_services.services.registry import ServiceRegistry
from app.services.camera_services.source.camera_source import CameraSource

logger = logging.getLogger(__name__)


def release_resources(camera: CameraSource, services: ServiceRegistry) -> None:
    """Release the camera, database connection, display window, and
    background sync worker held by a CameraPipeline."""
    if services.background_sync:
        services.background_sync.wait_until_empty()
        services.background_sync.stop()

    camera.release()

    # Close DB connection if provided by the registry (backwards compatible)
    if getattr(services, "db", None):
        try:
            services.db.close()
        except Exception:
            logger.exception("Failed to close DB connection")

    services.display_pipeline.close()


def print_summary(
    services: ServiceRegistry,
    original_size: Optional[tuple[int, int]],
    processed_size: tuple[int, int],
) -> None:
    """Print the final performance summary for the run."""
    services.performance.summary(
        original_resolution=original_size,
        processed_resolution=processed_size,
    )
